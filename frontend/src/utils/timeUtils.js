// Utility function for PKST time adjustment (+10 hours)
export const adjustTimeForPKST = (timeString) => {
  try {
    // Parse time string like "2:30 PM" or "9:00 AM"
    const match = timeString.match(/(\d{1,2}):?(\d{0,2})\s*(AM|PM)/i);
    if (!match) return timeString;

    let hours = parseInt(match[1]);
    const minutes = match[2] ? parseInt(match[2]) : 0;
    const period = match[3].toUpperCase();

    // Convert to 24-hour format
    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;

    // Add 10 hours for PKST adjustment
    hours = (hours + 10) % 24;

    // Convert back to 12-hour format
    const displayPeriod = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;

    return `${displayHours}:${String(minutes).padStart(2, '0')} ${displayPeriod}`;
  } catch (error) {
    return timeString;
  }
};
