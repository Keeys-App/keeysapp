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
   * Total virtual height (from virtualizer.getTotalSize())
   */
  totalHeight: number;
  
  /**
   * Additional className
   */
  className?: string;
}

export function CustomScrollbar({
  scrollContainerRef,
  totalItems,
  totalHeight,
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
  const dragOffsetY = useRef(0); // Offset from thumb top to mouse position
  
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
    
    // Calculate offset from top of thumb to mouse position
    if (thumbRef.current) {
      const thumbRect = thumbRef.current.getBoundingClientRect();
      dragOffsetY.current = e.clientY - thumbRect.top;
    }
  }, [scrollPosition]);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !scrollContainerRef.current || !scrollbarRef.current) {
        return;
      }

      // Calculate position relative to scrollbar
      const rect = scrollbarRef.current.getBoundingClientRect();
      const mouseY = e.clientY - rect.top;
      
      // Calculate the top position of thumb (where user clicked - offset)
      const thumbTopPosition = mouseY - dragOffsetY.current;
      
      // The scrollable range for the thumb (accounting for padding)
      const scrollableRange = visibleHeight - thumbHeight - (thumbPadding * 2);
      
      // Thumb position relative to the start of scrollable area
      const relativeThumbTop = thumbTopPosition - thumbPadding;
      
      // Clamp the position to valid range
      const clampedPosition = Math.max(0, Math.min(scrollableRange, relativeThumbTop));
      
      // Calculate percentage and apply to content
      const scrollPercentage = scrollableRange > 0 ? clampedPosition / scrollableRange : 0;
      const newScrollTop = scrollPercentage * (totalHeight - visibleHeight);

      scrollContainerRef.current.scrollTop = Math.max(0, Math.min(totalHeight - visibleHeight, newScrollTop));
    },
    [isDragging, scrollContainerRef, visibleHeight, thumbHeight, totalHeight, thumbPadding]
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
      
      // Calculate where the box would be positioned (centered on click)
      const previewTop = clickY - (thumbHeight / 2);
      const clampedTop = Math.max(thumbPadding, Math.min(visibleHeight - thumbHeight - thumbPadding, previewTop));
      
      // Calculate scroll position based on the box position
      const scrollableRange = visibleHeight - thumbHeight - (thumbPadding * 2);
      const boxPositionInRange = clampedTop - thumbPadding;
      const scrollPercentage = scrollableRange > 0 ? boxPositionInRange / scrollableRange : 0;
      const newScrollTop = scrollPercentage * (totalHeight - visibleHeight);

      scrollContainerRef.current.scrollTop = newScrollTop;
    },
    [scrollContainerRef, totalHeight, visibleHeight, thumbHeight, thumbPadding]
  );

  // Check if scrollbar should be disabled (all content is visible)
  const isDisabled = totalHeight <= visibleHeight;

  // Calculate visible item range
  const firstVisibleItem = Math.floor((scrollPosition / totalHeight) * totalItems) + 1;
  const lastVisibleItem = Math.min(
    Math.ceil(((scrollPosition + visibleHeight) / totalHeight) * totalItems),
    totalItems
  );

  // Calculate hover preview range
  let hoverPreviewRange: { start: number; end: number; top: number; height: number } | null = null;
  if (hoverPosition !== null && !isDisabled) {
    // Calculate visual position of the preview box with padding
    const previewTop = hoverPosition - (thumbHeight / 2);
    const clampedTop = Math.max(thumbPadding, Math.min(visibleHeight - thumbHeight - thumbPadding, previewTop));
    
    // Calculate scroll position based on the box position (not mouse position)
    const scrollableRange = visibleHeight - thumbHeight - (thumbPadding * 2);
    const boxPositionInRange = clampedTop - thumbPadding;
    const scrollPercentage = scrollableRange > 0 ? boxPositionInRange / scrollableRange : 0;
    const previewScrollTop = scrollPercentage * (totalHeight - visibleHeight);
    
    // Calculate item range based on the box position
    const hoverFirstItem = Math.floor((previewScrollTop / totalHeight) * totalItems) + 1;
    const hoverLastItem = Math.min(
      Math.ceil(((previewScrollTop + visibleHeight) / totalHeight) * totalItems),
      totalItems
    );
    
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
        isHovered && !isDragging && !isDisabled ? "w-16 backdrop-blur-xs" : "w-3",
        isDisabled && "opacity-30 pointer-events-none",
        className
      )}
      onClick={isDisabled ? undefined : handleTrackClick}
      onMouseMove={isDisabled ? undefined : handleTrackMouseMove}
      onMouseLeave={isDisabled ? undefined : handleTrackMouseLeave}
      onMouseEnter={isDisabled ? undefined : handleTrackMouseEnter}
    >
      {/* Position indicators - only show on hover */}
      {isHovered && !isDragging ? (
        <div className="absolute inset-0 flex flex-col justify-between py-2 px-2 pointer-events-none">
          {/* First item */}
          <div className="text-[11px] font-mono text-muted-foreground text-right">
            1
          </div>
          
          {/* Current position */}
          {firstVisibleItem > 0 && lastVisibleItem <= totalItems ? (
            <div
              className="text-[11px] font-mono font-medium text-foreground text-right bg-primary/10 dark:bg-primary/60 px-1 rounded"
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
          <div className="absolute left-1 top-1/2 -translate-y-1/2 text-[11px] font-mono font-medium text-primary bg-background/90 px-1 ml-[1px] rounded whitespace-nowrap">
            {hoverPreviewRange.start}
          </div>
        </div>
      ) : null}

      {/* Scrollbar thumb - only show when not disabled */}
      {!isDisabled ? (
        <div
          ref={thumbRef}
          className={cn(
            "absolute right-[2px] w-[7px] rounded-[3px] transition-colors",
            isDragging 
              ? "bg-gray-400 dark:bg-gray-500 cursor-grabbing" 
              : "bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 cursor-grab"
          )}
          style={{
            height: `${thumbHeight}px`,
            top: `${thumbTop}px`,
          }}
          onMouseDown={handleMouseDown}
        />
      ) : null}
    </div>
  );
}

