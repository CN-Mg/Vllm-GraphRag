import { useMemo } from 'react';
import { Menu } from '@neo4j-ndl/react';
import { useFileContext } from '../../context/UsersFiles';
import { chatModes } from '../../utils/Constants';
import { capitalize } from '@mui/material';
import { createPortal } from 'react-dom';

export default function ChatModeToggle({
  menuAnchor,
  closeHandler = () => {},
  open,
  anchorPortal = true,
  disableBackdrop = false,
}: {
  menuAnchor: HTMLElement | null;
  closeHandler?: () => void;
  open: boolean;
  anchorPortal?: boolean;
  disableBackdrop?: boolean;
}) {
  const { setchatMode, chatMode } = useFileContext();

  // Debug: log chatModes and open status
  console.log('ChatModeToggle - chatModes:', chatModes, 'open:', open, 'menuAnchor:', menuAnchor);

  const getModeTitle = (mode: string): string => {
    if(mode === 'image+graph+vector')
    {
      return 'Image + Graph + Vector';
    }
    if (mode.includes('+')) {
      return mode.replace('+', ' + ');
    }
    return capitalize(mode);
  };

  const items = useMemo(
    () =>
      chatModes?.map((m) => {
        return {
          title: getModeTitle(m),
          onClick: () => {
            console.log('Chat mode selected:', m);
            setchatMode(m);
            closeHandler();
          },
          disabledCondition: false,
          isSelected: chatMode === m,
          selectedClassName: 'n-bg-palette-primary-bg-weak',
        };
      }),
    [chatMode, chatModes, closeHandler]
  );

  console.log('ChatModeToggle - items:', items);
  console.log('ChatModeToggle - menuAnchor:', menuAnchor);
  console.log('ChatModeToggle - open:', open);

  return (
    <Menu
      open={open}
      onClose={closeHandler}
      anchorEl={menuAnchor}
    >
      {items && items.length > 0 ? (
        items?.map((item, idx) => (
          <Menu.Item
            key={idx}
            title={item.title}
            onClick={() => {
              console.log('Menu.Item clicked:', item.title);
              item.onClick();
            }}
            disabled={item.disabledCondition}
            selected={item.isSelected}
          />
        ))
      ) : (
        <Menu.Item
          key='fallback'
          title='No modes available'
          onClick={() => {}}
          disabled={true}
        />
      )}
    </Menu>
  );
}
