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
  const [hoverPosition, setHoverPosition] = useState<number | null>(null);
  const [isHovered, setIsHovered] = useState(false);
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
  
  // Padding for thumb from top and bottom
  const thumbPadding = 2;
  
  // Calculate scroll position as percentage
  const scrollPercentage = scrollPosition / (totalHeight - visibleHeight);
  const thumbTop = thumbPadding + (scrollPercentage * (visibleHeight - thumbHeight - thumbPadding * 2));

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
      const scrollDelta = (deltaY / (visibleHeight - thumbHeight - thumbPadding * 2)) * (totalHeight - visibleHeight);
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

  // Handle mouse move on scrollbar track
  const handleTrackMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!scrollbarRef.current) {
        return;
      }

      const rect = scrollbarRef.current.getBoundingClientRect();
      const mouseY = e.clientY - rect.top;
      setHoverPosition(mouseY);
    },
    []
  );

  const handleTrackMouseLeave = useCallback(() => {
    setHoverPosition(null);
    setIsHovered(false);
  }, []);

  const handleTrackMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  // Handle click on scrollbar track
  const handleTrackClick = useCallback(
    (e: React.MouseEvent) => {
      if (!scrollbarRef.current || !scrollContainerRef.current) {
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

  // Calculate visible item range
  const firstVisibleItem = Math.floor((scrollPosition / totalHeight) * totalItems) + 1;
  const lastVisibleItem = Math.min(
    Math.ceil(((scrollPosition + visibleHeight) / totalHeight) * totalItems),
    totalItems
  );

  // Calculate hover preview range
  let hoverPreviewRange: { start: number; end: number; top: number; height: number } | null = null;
  if (hoverPosition !== null) {
    const hoverScrollPercentage = hoverPosition / visibleHeight;
    const hoverScrollTop = hoverScrollPercentage * (totalHeight - visibleHeight);
    const hoverFirstItem = Math.floor((hoverScrollTop / totalHeight) * totalItems) + 1;
    const hoverLastItem = Math.min(
      Math.ceil(((hoverScrollTop + visibleHeight) / totalHeight) * totalItems),
      totalItems
    );
    
    // Calculate visual position of the preview box with padding
    const previewTop = hoverPosition - (thumbHeight / 2);
    const clampedTop = Math.max(thumbPadding, Math.min(visibleHeight - thumbHeight - thumbPadding, previewTop));
    
    hoverPreviewRange = {
      start: hoverFirstItem,
      end: hoverLastItem,
      top: clampedTop,
      height: thumbHeight,
    };
  }

  return (
    <div
      ref={scrollbarRef}
      className={cn(
        "absolute right-0 top-0 bottom-0 transition-all bg-background/50 border-l border-l-border",
        isHovered && !isDragging ? "w-16 backdrop-blur-xs" : "w-3",
        className
      )}
      onClick={handleTrackClick}
      onMouseMove={handleTrackMouseMove}
      onMouseLeave={handleTrackMouseLeave}
      onMouseEnter={handleTrackMouseEnter}
    >
      {/* Position indicators - only show on hover */}
      {isHovered && !isDragging ? (
        <div className="absolute inset-0 flex flex-col justify-between py-2 px-2 pointer-events-none">
          {/* First item */}
          <div className="text-[11px] font-mono text-muted-foreground text-right">
            1
          </div>
          
          {/* Current position */}
          {firstVisibleItem > 1 && lastVisibleItem < totalItems ? (
            <div
              className="text-[11px] font-mono font-medium text-foreground text-right bg-primary/10 px-1 rounded"
              style={{
                position: "absolute",
                top: `${thumbTop + thumbHeight / 2 - 8}px`,
              }}
            >
              {firstVisibleItem}
            </div>
          ) : null}
          
          {/* Last item */}
          <div className="text-[11px] font-mono text-muted-foreground text-right">
            {totalItems}
          </div>
        </div>
      ) : null}

      {/* Hover preview range box */}
      {hoverPreviewRange && !isDragging ? (
        <div
          className="absolute left-[2px] right-[2px] border-1 box-border border-primary/60 bg-primary/10 rounded pointer-events-none"
          style={{
            top: `${hoverPreviewRange.top}px`,
            height: `${hoverPreviewRange.height}px`,
          }}
        >
          <div className="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] font-mono font-medium text-primary bg-background/90 px-1.5 py-0.5 rounded whitespace-nowrap">
            {hoverPreviewRange.start}
          </div>
        </div>
      ) : null}

      {/* Scrollbar thumb */}
      <div
        ref={thumbRef}
        className={cn(
          "absolute right-[2px] w-[7px] rounded-[3px] overflow-hidden cursor-grab",
          isDragging ? "bg-primary/40 cursor-grabbing" : "bg-primary/40"
        )}
        style={{
          height: `${thumbHeight}px`,
          top: `${thumbTop}px`,
        }}
        onMouseDown={handleMouseDown}
      >
        {/* Progress indicator inside thumb */}
        <div
          className="absolute inset-0 rounded-[2px] bg-primary"
          style={{
            height: `${(loadedItems / totalItems) * 100}%`,
          }}
        />
      </div>
    </div>
  );
}

