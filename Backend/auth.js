const firebaseConfig = {
    apiKey: "AIzaSyD24Sfv8QG_YD1aaGMCOF-DlnGv6VWjnek",
    authDomain: "esd-project-listing.firebaseapp.com",
    projectId: "esd-project-listing",
    appId: "1:877925820233:web:0c468f7d123ccc39145c98"
  };
  
  firebase.initializeApp(firebaseConfig);
  
  
  firebase.auth().onAuthStateChanged(function(user) {
      if (user) {

        // user.getIdToken().then(function(token) {
        //   // Use the token here
        //   console.log(token)
        //   sessionStorage.setItem('token', token);
        //   userid = user.uid
        //   sessionStorage.setItem('userid', userid);
        //   console.log(userid)
        // }).catch(function(error) {
        //   // Handle error here
        //   console.log(error.message)
        // });
        
        userid = user.uid;
        sessionStorage.setItem('userid', userid);
        api = 'reader';
        sessionStorage.setItem('api', api);
        console.log(userid, ", API Key:", api);
      }
  });
  
  
  function login(){
    event.preventDefault()
    email = document.getElementById('email').value
    password = document.getElementById('password').value
    firebase.auth().signInWithEmailAndPassword(email,password)
      .then(function(){
          // user = firebase.auth().currentUser
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