import config
from utils import save_plot
import tensorflow as tf
from keras.datasets import cifar10
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
import kerastuner as kt
from sklearn.metrics import classification_report

seed = 42
weight_decay = 0.0001

(x_train, y_train), (x_test, y_test) = cifar10.load_data()


def normalize(x):
    x = x.astype('float32')
    x = x / 255.0
    return x


datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
)

x_test, x_val, y_test, y_val = train_test_split(x_test, y_test, test_size=0.5, random_state=0)

x_train = normalize(x_train)
x_test = normalize(x_test)
x_val = normalize(x_val)
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)
y_val = tf.keras.utils.to_categorical(y_val, 10)

datagen.fit(x_train)


def build(hp):
    model = Sequential([
        Conv2D(hp.Int("conv_1", min_value=64, max_value=128, step=64), (3, 3), activation='relu', padding='same',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), input_shape=config.INPUT_SHAPE),
        BatchNormalization(),
        Conv2D(hp.Int("conv_2", min_value=64, max_value=128, step=64), (3, 3), activation='relu',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.2),
        Conv2D(hp.Int("conv_3", min_value=128, max_value=256, step=128), (3, 3), activation='relu',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), padding='same'),
        BatchNormalization(),
        Conv2D(hp.Int("conv_4", min_value=128, max_value=256, step=128), (3, 3), activation='relu',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        Conv2D(hp.Int("conv_5", min_value=256, max_value=512, step=256), (3, 3), activation='relu',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), padding='same'),
        BatchNormalization(),
        Conv2D(hp.Int("conv_5", min_value=256, max_value=512, step=256), (3, 3), activation='relu',
               kernel_regularizer=tf.keras.regularizers.l2(weight_decay), padding='same'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),
        Dropout(0.3),
        Flatten(),
        Dense(256, activation='relu'),
        Dense(config.NUM_CLASSES, activation='softmax')
    ])
    lr = hp.Choice("learning_rate",
                   values=[0.001, 0.01])
    opt = tf.keras.optimizers.SGD(learning_rate=lr, momentum=0.9)
    # compile the model
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    # return the model
    return model


def find_best_model():
    es = EarlyStopping(
        monitor="val_loss",
        patience=config.EARLY_STOPPING,
        restore_best_weights=True)

    print("[INFO] instantiating a hyperband tuner object...")
    tuner = kt.Hyperband(
        build,
        objective="val_accuracy",
        max_epochs=config.EPOCHS,
        factor=3,
        seed=42,
        directory=config.OUTPUT_PATH,
        project_name="Image Classification")

    print("[INFO] performing hyperparameter search...")
    tuner.search(x=x_train, y=y_train,
                 validation_data=(x_train, y_train),
                 batch_size=config.BATCH_SIZE,
                 callbacks=[es],
                 epochs=config.EPOCHS
                 )
    # grab the best hyperparameters
    bestHP = tuner.get_best_hyperparameters(num_trials=1)[0]
    print("[INFO] optimal number of filters in conv_1 layer: {}".format(bestHP.get("conv_1")))
    print("[INFO] optimal number of filters in conv_2 layer: {}".format(bestHP.get("conv_2")))
    print("[INFO] optimal number of filters in conv_2 layer: {}".format(bestHP.get("conv_3")))
    print("[INFO] optimal number of filters in conv_2 layer: {}".format(bestHP.get("conv_4")))
    print("[INFO] optimal number of filters in conv_2 layer: {}".format(bestHP.get("conv_5")))
    print("[INFO] optimal learning rate: {:.4f}".format(bestHP.get("learning_rate")))

    print("[INFO] training the best model...")
    model = tuner.hypermodel.build(bestHP)
    H = model.fit(x=x_train, y=y_train,
                  validation_data=(x_test, y_test), batch_size=config.BATCH_SIZE,
                  epochs=config.EPOCHS, callbacks=[es], verbose=1)
    # evaluate the network
    print("[INFO] evaluating network...")
    predictions = model.predict(x=x_test, batch_size=32)
    print(classification_report(y_test.argmax(axis=1), predictions.argmax(axis=1)))
    # generate the training loss/accuracy plot
    save_plot(H, "../output")


find_best_model()
# def results(model):
#     epoch = 100
#     r = model.fit(datagen.flow(x_train, y_train, batch_size=32), epochs=epoch, steps_per_epoch=len(x_train) // 32,
#                   validation_data=(x_val, y_val), verbose=1)
#     acc = model.evaluate(x_test, y_test)
#     print("test set loss : ", acc[0])
#     print("test set accuracy :", acc[1] * 100)
#     epoch_range = range(1, epoch + 1)
#     plt.plot(epoch_range, r.history['accuracy'])
#     plt.plot(epoch_range, r.history['val_accuracy'])
#     plt.title('Classification Accuracy')
#     plt.ylabel('Accuracy')
#     plt.xlabel('Epoch')
#     plt.legend(['Train', 'Val'], loc='lower right')
#     plt.show()
#     # Plot training & validation loss values
#     plt.plot(epoch_range, r.history['loss'])
#     plt.plot(epoch_range, r.history['val_loss'])
#     plt.title('Model loss')
#     plt.ylabel('Loss')
#     plt.xlabel('Epoch')
#     plt.legend(['Train', 'Val'], loc='lower right')
#     plt.show()
#
#
# results(model)
