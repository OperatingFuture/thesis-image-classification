echo '################ MONGO ENTRYPOINT START ################';

mongo -- "$INITDB" <<EOF
db = db.getSiblingDB($INITDB);
db.createUser(
  {
    user: '$INIT_USERNAME',
    pwd: '$INIT_PWD',
    roles: [{ role: 'readWrite', db: '$INITDB' }],
  },
);
db.createCollection('$MONGO_COLLECTION');
EOF

echo '################ MONGO ENTRYPOINT END ################';