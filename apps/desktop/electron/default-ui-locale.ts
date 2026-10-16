/** The UI language this build starts in while `display.language` is unset. This Vietnamese build
 *  ships `vi` (upstream ships none and follows the OS). The renderer reads it from the machine
 *  profile and saves it once so the backend follows; the native menus start in it before the
 *  renderer reports its language. */
export const DEFAULT_UI_LOCALE = 'vi'
