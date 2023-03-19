const firebaseConfig = {
  apiKey: "AIzaSyCgKc1xonEp5sma8rnGWtMIXAsnryW4pW8",
  authDomain: "bidbuddy-dc913.firebaseapp.com",
  projectId: "bidbuddy-dc913",
  appId: "1:16994765557:web:efbe2bdb34b772e4f0d3bc"
};

firebase.initializeApp(firebaseConfig);


firebase.auth().onAuthStateChanged(function(user) {
    if (user) {
      user.getIdToken().then(function(token) {
        // Use the token here
        console.log(token)
        sessionStorage.setItem('token', token);
        userid = user.uid
        sessionStorage.setItem('userid', userid);
        console.log(userid)
      }).catch(function(error) {
        // Handle error here
        console.log(error.message)
      });
    }
});


function login(){
  event.preventDefault()
  email = document.getElementById('email').value
  password = document.getElementById('password').value
  firebase.auth().signInWithEmailAndPassword(email,password)
    .then(function(){
        user = firebase.auth().currentUser
        console.log("Logged In")
    })
    .catch(function(error){
        console.log(error.message)
    })
}

function logout(){
  event.preventDefault()
  firebase.auth().signOut()
  .then(function(){
    console.log("Logged Out")
    sessionStorage.clear();
  })
  .catch(function(error){
      console.log(error.message)
  })
}

const button = document.getElementById('li');
button.addEventListener('click', login);

const button2 = document.getElementById('lo');
button2.addEventListener('click', logout);