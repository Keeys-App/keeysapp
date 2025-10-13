import { useState, useEffect, useRef, type FC } from 'react';
import { useSavingStore } from '@/stores';
import { Spinner } from '@/components/ui/spinner';
import { cn } from '@/lib/utils';

export const SavingIndicator: FC = () => {
  const { isSaving, savingMessage } = useSavingStore();
  
  const [shouldRenderFooter, setShouldRenderFooter] = useState(false);
  const [isFooterVisible, setIsFooterVisible] = useState(false);
  const showStartTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (isSaving) {
      // Show footer immediately when saving starts
      setShouldRenderFooter(true);
      showStartTimeRef.current = Date.now();
      // Add small delay for animation
      const showTimer = setTimeout(() => setIsFooterVisible(true), 10);
      return () => clearTimeout(showTimer);
    } else if (showStartTimeRef.current !== null) {
      // Calculate how long the footer has been shown
      const elapsedTime = Date.now() - showStartTimeRef.current;
      const minShowTime = 1000; // 1 second minimum
      const remainingTime = Math.max(0, minShowTime - elapsedTime);
      
      // Wait for minimum show time + 100ms delay before starting hide animation
      const delayTimer = setTimeout(() => {
        setIsFooterVisible(false);
      }, remainingTime + 100);
      
      // Wait for delay + animation to complete before removing from DOM
      const hideTimer = setTimeout(() => {
        setShouldRenderFooter(false);
        showStartTimeRef.current = null;
      }, remainingTime + 100 + 300);
      
      return () => {
        clearTimeout(delayTimer);
        clearTimeout(hideTimer);
      };
    }
  }, [isSaving]);

  if (!shouldRenderFooter) {
    return null;
  }

  return (
    <footer 
      className={cn(
        'bg-background h-12 border-t box-border sticky z-10 bottom-0 flex shrink-0 items-center gap-2 px-4 py-4',
        'transition-all duration-300 ease-in-out',
        isFooterVisible 
          ? 'opacity-100 translate-y-0' 
          : 'opacity-0 translate-y-2'
      )}
    >
      <Spinner />
      <span className="text-sm">{savingMessage}</span>
    </footer>
  );
};

