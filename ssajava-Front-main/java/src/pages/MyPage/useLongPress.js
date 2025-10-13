import { useCallback, useRef } from 'react';

const useLongPress = (
  onClick,
  onLongPress,
  { delay = 300 } = {}
) => {
  const timeout = useRef();
  const target = useRef();

  const start = useCallback(
    (event) => {
      // 오른쪽 클릭 방지
      if (event.button && event.button !== 0) return;
      
      target.current = event.currentTarget;
      timeout.current = setTimeout(() => {
        onLongPress(event);
        target.current = null;
      }, delay);
    },
    [onLongPress, delay]
  );

  const clear = useCallback(
    (event) => {
      timeout.current && clearTimeout(timeout.current);
      if (target.current) {
        onClick(event);
      }
      target.current = null;
    },
    [onClick]
  );

  return {
    onMouseDown: (e) => start(e),
    onTouchStart: (e) => start(e),
    onMouseUp: (e) => clear(e),
    onMouseLeave: (e) => { timeout.current && clearTimeout(timeout.current); target.current = null; },
    onTouchEnd: (e) => clear(e),
  };
};

export default useLongPress;