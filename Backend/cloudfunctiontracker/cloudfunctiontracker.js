// NOTE THAT THIS FILE CANNOT RUN ON ITS OWN BECAUSE I DID NOT ADD THE DEPENDENCIES ETC

const functions = require("firebase-functions");

const admin = require("firebase-admin");

const serviceAccount = require("./firebasekey.json");

const {CloudTasksClient} = require("@google-cloud/tasks");


admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

// const db = admin.firestore();

// exports.scheduledFunction = functions
//     .pubsub.schedule("* * * * *").onRun((context) => {
//       db
//           .collection("listings")
//           .doc("npnwi4PnC9llxboPZhM2")
//           // .update({"timestamp": admin.firestore.Timestamp.now()});
//           .update({"transaction_status": "closed"});

//       // return console.log("Updated", admin.firestore.Timestamp.now());
//       return console.log("Updated", admin.firestore.Timestamp.now());
//     });


exports.onCreatePost = functions.firestore.document("/listings/{id}").onCreate(async (snapshot) => {
  console.log("Oncreate function triggered!");
  const data = snapshot.data();
  console.log(data);
  const expiresIn = data["expiresIn"];
  const expiresAt = data["auction_end_datetime"];
  // const {expiresIn, expiresAt} = data;

  let expirationAtSeconds;
  if (expiresIn && expiresIn > 0) {
    expirationAtSeconds = Date.now() / 1000 + expiresIn;
  } else if (expiresAt) {
    expirationAtSeconds = expiresAt;
  }

  if (!expirationAtSeconds) {
    // No expiration set on this document, nothing to do
    return;
  }

  // Get the project ID from the FIREBASE_CONFIG env var
  const project = JSON.parse(process.env.FIREBASE_CONFIG).projectId;
  // const location = "asia-southeast1";
  const locationQueue = "asia-southeast1";
  const queue = "firestore-ttl";
  const locationCloudfunction = "us-central1";

  const tasksClient = new CloudTasksClient();
  const queuePath = tasksClient.queuePath(project, locationQueue, queue);

  const url = `https://${locationCloudfunction}-${project}.cloudfunctions.net/firestoreTtlCallback`;
  const docPath = snapshot.ref.path;
  const payload = {docPath};

  const task = {
    httpRequest: {
      httpMethod: "POST",
      url,
      body: Buffer.from(JSON.stringify(payload)).toString("base64"),
      headers: {
        "Content-Type": "application/json",
      },
    },
    scheduleTime: {
      seconds: expirationAtSeconds,
    },
  };

  await tasksClient.createTask({parent: queuePath, task});

  // const [response] = await tasksClient.createTask({parent: queuePath, task});

  // const expirationTask = response.name;
  // const update = {expirationTask};
  // await snapshot.ref.update(update);
});


exports.firestoreTtlCallback = functions.https.onRequest(async (req, res) => {
  const payload = req.body;
  try {
    await admin.firestore().doc(payload.docPath).update({"status": "closed"});
    res.send(200);
  } catch (error) {
    console.error(error);
    res.status(500).send(error);
  }
});
