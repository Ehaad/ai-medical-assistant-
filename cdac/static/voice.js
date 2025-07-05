function speak(text) {
    const utterance = new SpeechSynthesisUtterance();
    utterance.text = text.replace(/<[^>]+>/g, '');
    utterance.lang = "en-US";
    utterance.pitch = 1;
    utterance.rate = 1;
    speechSynthesis.speak(utterance);
}
