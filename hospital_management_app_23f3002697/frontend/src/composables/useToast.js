/**
 * Toast notification composable
 * Usage:
 *   const toast = useToast();
 *   toast.success('Success', 'Operation completed');
 *   toast.error('Error', 'Something went wrong');
 */
export function useToast() {
  const showToast = (type, title, message, duration = 5000) => {
    if (window.$toast) {
      window.$toast[type](title, message, duration);
    } else {
      // Fallback to console if toast not initialized
      console[type === 'error' ? 'error' : 'log'](`${title}: ${message}`);
    }
  };

  return {
    success: (title, message, duration) => showToast('success', title, message, duration),
    error: (title, message, duration) => showToast('error', title, message, duration),
    warning: (title, message, duration) => showToast('warning', title, message, duration),
    info: (title, message, duration) => showToast('info', title, message, duration),
    clear: () => {
      if (window.$toast) {
        window.$toast.clear();
      }
    }
  };
}

