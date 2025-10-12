import { useEffect, useRef, useState, useCallback } from "react";
import { cn } from "@/lib/utils";

interface CustomScrollbarProps {
  /**
   * Reference to the scrollable container
   */
  scrollContainerRef: React.RefObject<HTMLDivElement | null>;
  
  /**
   * Total number of items (for calculating proportions)
   */
  totalItems: number;
  
  /**
   * Number of currently loaded items
   */
  loadedItems: number;
  
  /**
   * Height of a single item (for calculations)
   */
  itemHeight: number;
  
  /**
   * Additional className
   */
  className?: string;
}

export function CustomScrollbar({
  scrollContainerRef,
  totalItems,
  loadedItems,
  itemHeight,
  className,
}: CustomScrollbarProps) {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const scrollbarRef = useRef<HTMLDivElement>(null);
  const thumbRef = useRef<HTMLDivElement>(null);
  const dragStartY = useRef(0);
  const dragStartScrollTop = useRef(0);

  // Calculate total virtual height
  const totalHeight = totalItems * itemHeight;
  
  // Calculate visible height
  const visibleHeight = scrollContainerRef.current?.clientHeight || 0;
  
  // Calculate thumb height (proportional to visible content)
  const thumbHeightRatio = Math.min(1, visibleHeight / totalHeight);
  const thumbHeight = Math.max(50, thumbHeightRatio * visibleHeight);
  
  // Calculate scroll position as percentage
  const scrollPercentage = scrollPosition / (totalHeight - visibleHeight);
  const thumbTop = scrollPercentage * (visibleHeight - thumbHeight);

  // Update scroll position when container scrolls
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    const handleScroll = () => {
      setScrollPosition(container.scrollTop);
    };

    container.addEventListener("scroll", handleScroll);
    return () => {
      container.removeEventListener("scroll", handleScroll);
    };
  }, [scrollContainerRef]);

  // Handle thumb drag
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartY.current = e.clientY;
    dragStartScrollTop.current = scrollPosition;
  }, [scrollPosition]);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !scrollContainerRef.current) {
        return;
      }

      const deltaY = e.clientY - dragStartY.current;
      const scrollDelta = (deltaY / (visibleHeight - thumbHeight)) * (totalHeight - visibleHeight);
      const newScrollTop = Math.max(
        0,
        Math.min(totalHeight - visibleHeight, dragStartScrollTop.current + scrollDelta)
      );

      scrollContainerRef.current.scrollTop = newScrollTop;
    },
    [isDragging, scrollContainerRef, visibleHeight, thumbHeight, totalHeight]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      return () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  // Handle click on scrollbar track
  const handleTrackClick = useCallback(
    (e: React.MouseEvent) => {
      if (!scrollbarRef.current || !scrollContainerRef.current || e.target !== scrollbarRef.current) {
        return;
      }

      const rect = scrollbarRef.current.getBoundingClientRect();
      const clickY = e.clientY - rect.top;
      const scrollPercentage = clickY / rect.height;
      const newScrollTop = scrollPercentage * (totalHeight - visibleHeight);

      scrollContainerRef.current.scrollTop = newScrollTop;
    },
    [scrollContainerRef, totalHeight, visibleHeight]
  );

  // Don't show scrollbar if all content is visible
  if (totalHeight <= visibleHeight) {
    return null;
  }

  return (
    <div
      ref={scrollbarRef}
      className={cn(
        "absolute right-0 top-0 bottom-0 w-3 bg-transparent hover:bg-muted/30 transition-colors cursor-pointer",
        className
      )}
      onClick={handleTrackClick}
    >
      <div
        ref={thumbRef}
        className={cn(
          "absolute right-0.5 w-2 rounded-full bg-border hover:bg-foreground/40 transition-colors cursor-grab",
          isDragging && "bg-foreground/50 cursor-grabbing"
        )}
        style={{
          height: `${thumbHeight}px`,
          top: `${thumbTop}px`,
        }}
        onMouseDown={handleMouseDown}
      >
        {/* Progress indicator */}
        <div
          className="absolute inset-0 rounded-full bg-primary/60 transition-all"
          style={{
            height: `${(loadedItems / totalItems) * 100}%`,
          }}
        />
      </div>
      
      {/* Loading indicator */}
      {loadedItems < totalItems ? (
        <div
          className="absolute right-1 text-[10px] text-muted-foreground font-mono bg-background/80 px-1 rounded pointer-events-none"
          style={{
            top: `${thumbTop + thumbHeight / 2 - 8}px`,
          }}
        >
          {Math.round((loadedItems / totalItems) * 100)}%
        </div>
      ) : null}
    </div>
  );
}

