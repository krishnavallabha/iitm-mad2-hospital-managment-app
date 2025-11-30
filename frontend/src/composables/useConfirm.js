/**
 * Confirmation dialog composable
 * Usage:
 *   const confirm = useConfirm();
 *   try {
 *     await confirm.show({
 *       title: 'Delete Doctor',
 *       message: 'Are you sure you want to delete this doctor?',
 *       type: 'danger'
 *     });
 *     // User confirmed - proceed with action
 *   } catch {
 *     // User cancelled
 *   }
 */
import { ref } from 'vue';

let globalResolve = null;
let globalReject = null;

const dialogState = ref({
  visible: false,
  title: 'Confirm Action',
  message: '',
  details: '',
  type: 'warning',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loading: false
});

export function useConfirm() {
  const show = (options = {}) => {
    return new Promise((resolve, reject) => {
      globalResolve = resolve;
      globalReject = reject;
      
      dialogState.value = {
        visible: true,
        title: options.title || 'Confirm Action',
        message: options.message || 'Are you sure?',
        details: options.details || '',
        type: options.type || 'warning',
        confirmText: options.confirmText || 'Confirm',
        cancelText: options.cancelText || 'Cancel',
        loading: false
      };
    });
  };

  const hide = () => {
    dialogState.value.visible = false;
    if (globalReject) {
      globalReject(new Error('User cancelled'));
      globalReject = null;
      globalResolve = null;
    }
  };

  const confirm = () => {
    dialogState.value.visible = false;
    if (globalResolve) {
      globalResolve(true);
      globalResolve = null;
      globalReject = null;
    }
  };

  return {
    show,
    hide,
    confirm,
    state: dialogState
  };
}

