import React, { createContext, useCallback, useState } from 'react';

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
  const [swapRequests, setSwapRequests] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [lastNotification, setLastNotification] = useState(null);

  const updateSwapRequests = useCallback((requests) => {
    setSwapRequests(requests);
    setUnreadCount(requests.length);
  }, []);

  const markAsRead = useCallback(() => {
    setUnreadCount(0);
  }, []);

  const recordNotification = useCallback((notification) => {
    setLastNotification({
      timestamp: Date.now(),
      ...notification,
    });
  }, []);

  const value = {
    swapRequests,
    unreadCount,
    lastNotification,
    updateSwapRequests,
    markAsRead,
    recordNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext() {
  const context = React.useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotificationContext must be used within NotificationProvider');
  }
  return context;
}
