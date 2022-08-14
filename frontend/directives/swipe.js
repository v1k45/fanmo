import get from 'lodash/get';

/**
 * Taken and (very slightly) modified from
 * - https://stackoverflow.com/a/48255811
 * - https://github.com/john-doherty/swiped-events/blob/master/src/swiped-events.js
 */
const getTouchHandlers = (binding) => {
  let xDown = null;
  let yDown = null;
  let xDiff = null;
  let yDiff = null;
  let timeDown = null;
  let startEl = null;

  /**
   * Fires swiped event if swipe detected on touchend
   * @param {object} e - browser event object
   * @returns {void}
   */
  function handleTouchEnd(e) {
    // if the user released on a different target, cancel!
    if (startEl !== e.target) return;

    const swipeThreshold = get(binding, 'swipeThreshold', 20); // default 20px
    const swipeTimeout = get(binding, 'swipeTimeout', 500); // default 500ms
    const timeDiff = Date.now() - timeDown;
    let eventType = '';
    const changedTouches = e.changedTouches || e.touches || [];

    if (Math.abs(xDiff) > Math.abs(yDiff)) { // most significant
      if (Math.abs(xDiff) > swipeThreshold && timeDiff < swipeTimeout) {
        if (xDiff > 0) {
          eventType = 'swiped-left';
        } else {
          eventType = 'swiped-right';
        }
      }
    } else if (Math.abs(yDiff) > swipeThreshold && timeDiff < swipeTimeout) {
      if (yDiff > 0) {
        eventType = 'swiped-up';
      } else {
        eventType = 'swiped-down';
      }
    }

    if (eventType !== '') {
      const eventData = {
        dir: eventType.replace(/swiped-/, ''),
        touchType: (changedTouches[0] || {}).touchType || 'direct',
        xStart: parseInt(xDown, 10),
        xEnd: parseInt((changedTouches[0] || {}).clientX || -1, 10),
        yStart: parseInt(yDown, 10),
        yEnd: parseInt((changedTouches[0] || {}).clientY || -1, 10)
      };

      // fire `swiped` event event on the element that started the swipe
      startEl.dispatchEvent(new CustomEvent('swiped', { bubbles: true, cancelable: true, detail: eventData }));

      // fire `swiped-dir` event on the element that started the swipe
      startEl.dispatchEvent(new CustomEvent(eventType, { bubbles: true, cancelable: true, detail: eventData }));
    }

    // reset values
    xDown = null;
    yDown = null;
    timeDown = null;
  }

  /**
   * Records current location on touchstart event
   * @param {object} e - browser event object
   * @returns {void}
   */
  function handleTouchStart(e) {
    // if the element has data-swipe-ignore="true" we stop listening for swipe events
    if (e.target.closest('[data-swipe-ignore]')) return;

    startEl = e.target;

    timeDown = Date.now();
    xDown = e.touches[0].clientX;
    yDown = e.touches[0].clientY;
    xDiff = 0;
    yDiff = 0;
  }

  /**
   * Records location diff in px on touchmove event
   * @param {object} e - browser event object
   * @returns {void}
   */
  function handleTouchMove(e) {
    if (!xDown || !yDown) return;

    const xUp = e.touches[0].clientX;
    const yUp = e.touches[0].clientY;

    xDiff = xDown - xUp;
    yDiff = yDown - yUp;
  }

  return {
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd
  };
};

const unbindHandler = el => {
  if (!el.$swipeHandlers) return;
  Object.entries(el.$swipeHandlers).forEach(([eventName, handler]) => {
    document.removeEventListener(eventName, handler, false);
  });
  delete el.$swipeHandlers;
};

const bindUpdateHandler = (el, binding) => {
  const isEnabled = get(binding, 'enabled', true);
  if (!isEnabled) {
    unbindHandler(el);
    return;
  }
  const { handleTouchStart, handleTouchMove, handleTouchEnd } = getTouchHandlers(binding);
  el.$swipeHandlers = { touchstart: handleTouchStart, touchmove: handleTouchMove, touchend: handleTouchEnd };
  Object.entries(el.$swipeHandlers).forEach(([eventName, handler]) => {
    document.addEventListener(eventName, handler, false);
  });
};

export default {
  bind: bindUpdateHandler,
  update: bindUpdateHandler,
  unbind: unbindHandler
};
