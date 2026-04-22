/**
 * Notification utility functions
 */

/**
 * Request permission to send browser notifications
 */
export const requestNotificationPermission = () => {
  if (!('Notification' in window)) {
    console.log('Browser does not support notifications');
    return;
  }

  if (Notification.permission === 'granted') {
    console.log('Notification permission already granted');
    return;
  }

  if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        console.log('Notification permission granted');
      }
    });
  }
};

/**
 * Send a browser notification
 * @param {string} title - Notification title
 * @param {object} options - Notification options
 */
export const sendNotification = (title, options = {}) => {
  if (!('Notification' in window)) {
    console.log('Browser does not support notifications');
    return;
  }

  if (Notification.permission === 'granted') {
    const defaultOptions = {
      icon: 'ðŸ””',
      tag: 'swap-notification',
      requireInteraction: true,
      ...options,
    };

    new Notification(title, defaultOptions);
  }
};

/**
 * Play a notification sound using Web Audio API
 * @param {number} frequency - Frequency in Hz (default: 800)
 * @param {number} duration - Duration in seconds (default: 0.5)
 * @param {number} volume - Volume 0-1 (default: 0.3)
 */
export const playNotificationSound = (frequency = 800, duration = 0.5, volume = 0.3) => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
  } catch (err) {
    console.log('Could not play notification sound:', err);
  }
};

/**
 * Play a double beep sound for alerts
 */
export const playAlertSound = () => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // First beep
    const osc1 = audioContext.createOscillator();
    const gain1 = audioContext.createGain();
    osc1.connect(gain1);
    gain1.connect(audioContext.destination);
    osc1.frequency.value = 800;
    gain1.gain.setValueAtTime(0.3, audioContext.currentTime);
    gain1.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
    osc1.start(audioContext.currentTime);
    osc1.stop(audioContext.currentTime + 0.2);

    // Second beep (delayed)
    const osc2 = audioContext.createOscillator();
    const gain2 = audioContext.createGain();
    osc2.connect(gain2);
    gain2.connect(audioContext.destination);
    osc2.frequency.value = 900;
    gain2.gain.setValueAtTime(0.3, audioContext.currentTime + 0.3);
    gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    osc2.start(audioContext.currentTime + 0.3);
    osc2.stop(audioContext.currentTime + 0.5);
  } catch (err) {
    console.log('Could not play alert sound:', err);
  }
};
