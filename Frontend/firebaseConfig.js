import firebase from "firebase/compat/app";
import "firebase/compat/firestore";
import "firebase/compat/auth";
import { getFirestore } from "firebase/firestore";

// firebase init
const firebaseConfig = {
  apiKey: "AIzaSyCgKc1xonEp5sma8rnGWtMIXAsnryW4pW8",
  authDomain: "bidbuddy-dc913.firebaseapp.com",
  projectId: "bidbuddy-dc913",
  appId: "1:16994765557:web:efbe2bdb34b772e4f0d3bc",
};

const app = firebase.initializeApp(firebaseConfig);

// utils
const db = firebase.firestore();
const auth = firebase.auth();

// // export utils/refs
export { auth };
