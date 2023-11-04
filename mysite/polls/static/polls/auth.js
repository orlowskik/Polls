
function auth(){
    // Initialize the agent on page load.
  const fpPromise = import('https://fpjscdn.net/v3/pvsO3whAu7xuc36y8G3p')
    .then(FingerprintJS => FingerprintJS.load({
      region: "eu"
    }))

  // Get the visitorId when you need it.
  fpPromise
    .then(fp => fp.get())
    .then(result => {
        const visitorId = result.visitorId;
        console.log(visitorId);
        let form = document.getElementById('form');
        let authField = document.createElement('input');
        authField.setAttribute('type','text');
        authField.setAttribute('hidden', 'true');
        authField.setAttribute('name', 'userId');
        authField.setAttribute('value', visitorId)
        form.appendChild(authField);
        form.submit();
    })
    return true;
}




