import { IconButton, Tip } from '@neo4j-ndl/react';
import { forwardRef } from 'react';

const IconButtonWithToolTip = forwardRef<HTMLButtonElement, {
  text: string | React.ReactNode;
  children: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLButtonElement> | undefined;
  size?: 'small' | 'medium' | 'large';
  clean?: boolean;
  grouped?: boolean;
  placement?: 'bottom' | 'top' | 'right' | 'left';
  disabled?: boolean;
  label: string;
}>(
  ({ text, children, onClick, size = 'medium', clean, grouped, placement = 'bottom', disabled = false, label }, ref) => {
  return (
    <Tip allowedPlacements={[placement]}>
      <Tip.Trigger>
        <IconButton
          aria-label={label}
          size={size}
          clean={clean}
          grouped={grouped}
          onClick={onClick}
          disabled={disabled}
          ref={ref}
        >
          {children}
        </IconButton>
      </Tip.Trigger>
      <Tip.Content isPortaled={false} style={{ whiteSpace: 'nowrap' }}>
        {text}
      </Tip.Content>
    </Tip>
  );
});

IconButtonWithToolTip.displayName = 'IconButtonWithToolTip';

export default IconButtonWithToolTip;
