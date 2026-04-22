import { useEffect, useRef } from 'react';
import { useToast } from '../context/ToastContext';
import { useNotificationContext } from '../context/NotificationContext';
import { getSwapInbox } from '../services/api';

/**
 * Custom hook for real-time swap request notifications
 * Polls for new swap requests and shows notifications with sound and alerts
 * 
 * @param {boolean} enabled - Whether to enable polling (default: true)
 * @param {number} pollInterval - Polling interval in milliseconds (default: 2000)
 */
export function useNotifications(enabled = true, pollInterval = 2000) {
  const { showToast } = useToast();
  const { updateSwapRequests } = useNotificationContext();
  const previousCountRef = useRef(0);

  useEffect(() => {
    if (!enabled) return;

    // Request browser notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
          console.log('✓ Notification permission granted');
        }
      });
    }

    const pollSwapRequests = async () => {
      try {
        const response = await getSwapInbox();
        const swapRequests = Array.isArray(response.data) ? response.data : [];
        const currentCount = swapRequests.length;

        // Update global notification context
        updateSwapRequests(swapRequests);

        // Check if there are new requests
        if (currentCount > previousCountRef.current) {
          const newCount = currentCount - previousCountRef.current;

          // Play notification sound
          playNotificationSound();

          // Show toast notification
          const message = `You have ${newCount} new swap request${newCount > 1 ? 's' : ''}!`;
          showToast(message, 'info');

          // Show browser notification
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('🔔 SwapShift Alert', {
              body: message,
              icon: '/favicon.svg',
              tag: 'swap-request-notification',
              requireInteraction: true,
              badge: '/favicon.svg',
            });
          }
        }

        previousCountRef.current = currentCount;
      } catch (error) {
        console.error('Error polling swap requests:', error);
      }
    };

    // Initial poll
    pollSwapRequests();

    // Set up polling interval
    const interval = setInterval(pollSwapRequests, pollInterval);

    // Cleanup
    return () => clearInterval(interval);
  }, [enabled, pollInterval, showToast, updateSwapRequests]);
}

/**
 * Play a beep sound notification using Web Audio API
 * Frequency: 800Hz, Duration: 500ms
 */
function playNotificationSound() {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800; // 800Hz beep
    oscillator.type = 'sine';

    // Volume: 0.3 for 500ms
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  } catch (error) {
    console.log('Could not play notification sound:', error);
  }
}
