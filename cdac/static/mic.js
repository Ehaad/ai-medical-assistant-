function startDictation() {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        recognition.start();

        recognition.onresult = function (e) {
            document.getElementById("symptoms").value = e.results[0][0].transcript;
            recognition.stop();
            document.getElementById("diagnosisForm").dispatchEvent(new Event("submit"));
        };

        recognition.onerror = function () {
            recognition.stop();
        };
    } else {
        alert("Speech recognition not supported.");
    }
}
