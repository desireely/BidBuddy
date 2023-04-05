const functions = require("firebase-functions");

const admin = require("firebase-admin");

const serviceAccount = require("./firebasekey.json");
// const serviceAccount = require("./userCred (2).json");

const {CloudTasksClient} = require("@google-cloud/tasks");

const axios = require("axios");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});


exports.onCreatePost = functions.firestore.document("/listings/{id}").onCreate(async (snapshot) => {
  console.log("Oncreate function triggered!");
  const data = snapshot.data();
  console.log(data);
  const expiresIn = data["expiresIn"];
  const expiresAt = data["auction_end_datetime"];

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

  const url = `https://${locationCloudfunction}-${project}.cloudfunctions.net/firestoreCallbackCloseListing`;
  const docPath = snapshot.ref.path;
  const payload = {docPath};

  // First task to trigger track auction complex microservice when auction_end_datetime reaches
  console.log("TASK 1 IS RUNNING!");
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


  // // update transaction_end_datetime to 7 days later
  // // Add 7 days to auction_end_datetime
  console.log("TASK 2 IS RUNNING!");
  // // const numDays = 7;
  // // const transactionPeriodInSec = numDays * 24 * 60 * 60;
  // // const expirationAtSecondsForTransaction = expirationAtSeconds + transactionPeriodInSec;
  const expirationAtSecondsForTransaction = expirationAtSeconds + 90;

  // // const queue2 = "firestore-ttl-invoketracktransaction";

  await admin.firestore().doc(payload.docPath).update({"transaction_end_datetime": expirationAtSecondsForTransaction});
});


exports.firestoreCallbackCloseListing = functions.https.onRequest(async (req, res) => {
  const payload = req.body;
  try {
    await admin.firestore().doc(payload.docPath).update({"status": "closed"});
    res.send(200);

    console.log("Getting listing details");

    const listing = await admin.firestore().doc(payload.docPath).get();
    console.log(listing);
    const listingid = payload.docPath;
    console.log(listingid);
    // console.log(listing.data());
    // const listingName = listing["listing_name"];

    console.log("Listing_id is: ", listingid);
    // console.log("Listing name is: ", listingName);

    // 172.20.10.4
    axios.post("https://ee42-119-234-8-177.ap.ngrok.io/trackauction", {
      "listing_id": listingid,
    })
        .then((response) => {
          console.log(response.data);
        })
        .catch((error) => {
          console.log(error);
        });
  } catch (error) {
    console.error(error);
    res.status(500).send(error);
  }
});


exports.onUpdateListingClose = functions.firestore.document("/listings/{id}").onUpdate(async (change, context) => {
  console.log("OnUpdate function triggered!");
  // Get an object representing the document
  // e.g. {'name': 'Marie', 'age': 66}
  // const docPath = context.path;
  // console.log("docPath: ", docPath);

  console.log("Context is: ", context);

  const listingId = context.params.id;
  console.log("listingId is: ", listingId);

  const docPath = `listings/${listingId}`;
  console.log("docPath: ", docPath);

  const newValue = change.after.data();
  console.log("newValue is: ", newValue);

  // ...or the previous value before this update
  // const previousValue = change.before.data();

  // the value after an update operation
  const newStatus = newValue.status;
  console.log("newStatus is: ", newStatus);

  // the value before an update operation
  // const previousStatus = previousValue.status;

  const transactionEndDatetime = newValue.transaction_end_datetime;

  if (newStatus == "closed") {
    // There must be some changes
    // perform desired operations ...

    // Get the project ID from the FIREBASE_CONFIG env var
    const project = JSON.parse(process.env.FIREBASE_CONFIG).projectId;
    // const location = "asia-southeast1";
    const locationQueue = "asia-southeast1";
    const queue = "firestore-ttl";
    const locationCloudfunction = "us-central1";

    const tasksClient = new CloudTasksClient();
    const queuePath = tasksClient.queuePath(project, locationQueue, queue);

    const url = `https://${locationCloudfunction}-${project}.cloudfunctions.net/firestoreCallbackInvokeTrackTransaction`;

    const payload = {docPath};

    // First task to trigger track auction complex microservice when auction_end_datetime reaches
    console.log("TASK 2 IS RUNNING!");
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
        seconds: transactionEndDatetime,
      },
    };

    await tasksClient.createTask({parent: queuePath, task});
  } else {
  // No changes to the field called `name`
  // perform desired operations ...
    console.log("New status not closed!");
  }
});


exports.firestoreCallbackInvokeTrackTransaction = functions.https.onRequest(async (req, res) => {
  const payload = req.body;

  const listing = await admin.firestore().doc(payload.docPath).get();
  console.log(listing);
  const listingidpath = payload.docPath;
  console.log(listingidpath);
  const listingid = listingidpath.split("/")[1];
  console.log(listingid);
  // console.log(listing.data());
  // const listingName = listing["listing_name"];

  console.log("Listingid for firestoreCallbackInvokeTrackTransaction is: ", listingid);

  console.log("REACHED HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE!");

  // await admin.firestore().doc(payload.docPath).update({"transaction_status": "pending"});

  axios.post(`https://da75-119-234-8-177.ap.ngrok.io/checklisting/${listingid}`, {
    "listing_id": listingid,
  })
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
});
