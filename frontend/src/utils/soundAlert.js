export const playAlertSound = () => {
  // Create an audio context
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  
  // Ensure AudioContext is running if it was suspended by browser
  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }

  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);

  // Configure the first sound (alert)
  oscillator.frequency.value = 1800; // Frequency in Hz (800Hz for a sharp tone)
  oscillator.type = "sine"; // Sine wave sound (smooth tone)

  // Set the gain (volume)
  gainNode.gain.setValueAtTime(0.3, audioContext.currentTime); // Start volume
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5); // Fade out

  console.log("Alert sound playing...");

  // Start the oscillator
  oscillator.start(audioContext.currentTime);

  // Stop the oscillator after 1.5 seconds
  oscillator.stop(audioContext.currentTime + 1.5);

  // After the first sound finishes, play the second sound
  oscillator.onended = () => {
    console.log("First alert finished, playing second sound...");

    // Second sound (example: a different tone or effect)
    const secondOscillator = audioContext.createOscillator();
    const secondGainNode = audioContext.createGain();

    secondOscillator.connect(secondGainNode);
    secondGainNode.connect(audioContext.destination);

    secondOscillator.frequency.value = 1200; // A lower frequency for a different tone
    secondOscillator.type = "square"; // A different wave type (square for a different effect)

    secondGainNode.gain.setValueAtTime(0.3, audioContext.currentTime); // Start volume
    secondGainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5); // Fade out

    // Play the second sound
    secondOscillator.start(audioContext.currentTime);

    // Stop the second oscillator after 3 seconds
    secondOscillator.stop(audioContext.currentTime + 3);
  };
};



export const requestNotificationPermission = async () => {
  if ("Notification" in window && Notification.permission === "default") {
    await Notification.requestPermission();
  }
};

export const showNotification = (title, options) => {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, options);
  }
};

// Automatically trigger a "hidden" user gesture
export const simulateUserGesture = () => {
  // Create an invisible button or invoke a hidden click event
  const hiddenButton = document.createElement('button');
  hiddenButton.style.display = 'none';
  document.body.appendChild(hiddenButton);

  // Simulate a click after page load
  hiddenButton.click();
  document.body.removeChild(hiddenButton);
};
