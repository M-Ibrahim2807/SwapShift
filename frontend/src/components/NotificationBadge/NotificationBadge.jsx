import React, { useEffect, useState } from 'react';
import { Bell } from 'lucide-react';
import { useNotificationContext } from '../../context/NotificationContext';
import './NotificationBadge.css';

export default function NotificationBadge() {
  const { unreadCount } = useNotificationContext();
  const [isAnimating, setIsAnimating] = useState(false);
  const [prevCount, setPrevCount] = useState(unreadCount);

  useEffect(() => {
    if (unreadCount > prevCount) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 600);
      setPrevCount(unreadCount);
      return () => clearTimeout(timer);
    }
  }, [unreadCount, prevCount]);

  return (
    <div className={`notification-badge ${isAnimating ? 'animate' : ''}`}>
      <Bell size={20} className="notification-icon" />
      {unreadCount > 0 && (
        <span className="badge-count">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </div>
  );
}
