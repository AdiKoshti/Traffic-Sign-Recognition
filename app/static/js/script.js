document.getElementById('upload-btn').addEventListener('click', function () {
    let fileInput = document.getElementById('image-upload');
    let file = fileInput.files[0];
    let formData = new FormData();
    formData.append('file', file);

    fetch('/classify', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          document.getElementById('classified-sign').innerText = data.classified_sign;
      }).catch(error => {
          console.error('Error:', error);
      });
});

document.getElementById('translate-btn').addEventListener('click', function () {
    let text = document.getElementById('classified-sign').innerText;
    let lang = document.getElementById('language-select').value;

    fetch('/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text, lang: lang })
    }).then(response => response.json())
      .then(data => {
          document.getElementById('classified-sign').innerText = data.translated_text;
      }).catch(error => {
          console.error('Error:', error);
      });
});

async function speakSign() {
    const text = document.getElementById('classified-sign').textContent;

    if (!text) {
        alert('No text to speak.');
        return;
    }

    const response = await fetch('/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    if (data.audio) {
        const audio = new Audio('data:audio/mp3;base64,' + data.audio);
        audio.play();
    } else {
        alert(data.error);
    }
}


document.getElementById('start-camera').addEventListener('click', function () {
    fetch('/camera')
        .then(response => response.json())
        .then(data => {
            if (data.frame) {
                document.getElementById('camera-feed').src = 'data:image/jpeg;base64,' + data.frame;
            }
        }).catch(error => {
            console.error('Error:', error);
        });
});
