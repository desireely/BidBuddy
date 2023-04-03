import firebase from "firebase/compat/app";
import "firebase/compat/firestore";
import "firebase/compat/auth";
import { getFirestore } from "firebase/firestore";

// firebase init
const firebaseConfig = {
  apiKey: "AIzaSyD24Sfv8QG_YD1aaGMCOF-DlnGv6VWjnek",
  authDomain: "esd-project-listing.firebaseapp.com",
  projectId: "esd-project-listing",
  storageBucket: "esd-project-listing.appspot.com",
  messagingSenderId: "877925820233",
  appId: "1:877925820233:web:0c468f7d123ccc39145c98",
  measurementId: "G-CZY44KZTDJ"
};

const app = firebase.initializeApp(firebaseConfig);

// utils
const db = firebase.firestore();
const auth = firebase.auth();

// // export utils/refs
export { auth, db };
