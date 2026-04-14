import React, { useEffect, useState } from 'react';
import { Dialog, SideNavigation, Tip, IconButton } from '@neo4j-ndl/react';
import {
  ArrowRightIconOutline,
  ArrowLeftIconOutline,
  TrashIconOutline,
  ArrowsPointingOutIconOutline,
  ChatBubbleOvalLeftEllipsisIconOutline,
  CloudArrowUpIconSolid,
} from '@neo4j-ndl/react/icons';
import { SideNavProps } from '../../types';
import Chatbot from '../ChatBot/Chatbot';
import { createPortal } from 'react-dom';
import { useMessageContext } from '../../context/UserMessages';
import { getIsLoading } from '../../utils/Utils';
import ExpandedChatButtonContainer from '../ChatBot/ExpandedChatButtonContainer';
import { tooltips } from '../../utils/Constants';
import ChatModeToggle from '../ChatBot/ChatModeToggle';
import { RiChatSettingsLine } from 'react-icons/ri';

const SideNav: React.FC<SideNavProps> = ({
  position,
  toggleDrawer,
  isExpanded,
  deleteOnClick,
  setShowDrawerChatbot,
  setIsRightExpanded,
  messages,
  clearHistoryData,
}) => {
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const { setMessages } = useMessageContext();
  const [chatModeAnchor, setchatModeAnchor] = useState<HTMLElement | null>(null);
  const [showChatMode, setshowChatMode] = useState<boolean>(false);
  const date = new Date();
  useEffect(() => {
    if (clearHistoryData) {
      setMessages([
        {
          datetime: `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`,
          id: 2,
          message:
            ' 欢迎使用 LLM-Graph 模型对话功能。您可以询问与已完成处理的文档相关的问题。',
          user: 'chatbot',
        },
      ]);
    }
  }, [clearHistoryData]);

  const handleExpandClick = () => {
    setIsChatModalOpen(true);
    setIsFullScreen(true);
    if (setShowDrawerChatbot && setIsRightExpanded) {
      setShowDrawerChatbot(false);
      setIsRightExpanded(false);
    }
  };
  const handleShrinkClick = () => {
    setIsChatModalOpen(false);
    setIsFullScreen(false);
    if (setShowDrawerChatbot && setIsRightExpanded) {
      setShowDrawerChatbot(true);
      setIsRightExpanded(true);
    }
  };
  const handleClick = () => {
    toggleDrawer();
  };
  return (
    <div style={{ height: 'calc(100vh - 58px)', minHeight: '200px', display: 'flex' }}>
      <SideNavigation iconMenu={true} expanded={false} position={position}>
        <SideNavigation.List>
          <SideNavigation.Item
            onClick={handleClick}
            icon={
              isExpanded ? (
                position === 'left' ? (
                  <ArrowLeftIconOutline />
                ) : (
                  <ArrowRightIconOutline />
                )
              ) : position === 'left' ? (
                <>
                  <Tip allowedPlacements={['right']}>
                    <Tip.Trigger>
                      <CloudArrowUpIconSolid />
                    </Tip.Trigger>
                    <Tip.Content>{tooltips.sources}</Tip.Content>
                  </Tip>
                </>
              ) : (
                <>
                  <Tip allowedPlacements={['left']}>
                    <Tip.Trigger>
                      <ChatBubbleOvalLeftEllipsisIconOutline />
                    </Tip.Trigger>
                    <Tip.Content>{tooltips.chat}</Tip.Content>
                  </Tip>
                </>
              )
            }
          />

          {position === 'right' && isExpanded && (
            <>
              <Tip allowedPlacements={['left']}>
                <SideNavigation.Item
                  onClick={deleteOnClick}
                  icon={
                    <>
                      <Tip.Trigger>
                        <TrashIconOutline />
                      </Tip.Trigger>
                      <Tip.Content>{tooltips.clearChat}</Tip.Content>
                    </>
                  }
                />
              </Tip>
              <Tip allowedPlacements={['left']}>
                <SideNavigation.Item
                  onClick={handleExpandClick}
                  icon={
                    <>
                      <Tip.Trigger>
                        <ArrowsPointingOutIconOutline className='n-size-token-7' />
                      </Tip.Trigger>
                      <Tip.Content>{tooltips.maximise}</Tip.Content>
                    </>
                  }
                />
              </Tip>
              {!isChatModalOpen && (
                <SideNavigation.Item
                  icon={
                    <Tip allowedPlacements={['left']}>
                      <Tip.Trigger>
                        <IconButton
                          size='small'
                          clean
                          aria-label='Chat mode'
                          onClick={(e) => {
                            console.log('Chat mode button clicked - element:', e.currentTarget.tagName);
                            setchatModeAnchor(e.currentTarget as HTMLElement);
                            setshowChatMode(true);
                          }}
                        >
                          <RiChatSettingsLine className='n-size-token-7' />
                        </IconButton>
                      </Tip.Trigger>
                      <Tip.Content isPortaled={false} style={{ whiteSpace: 'nowrap' }}>
                        Chat mode
                      </Tip.Content>
                    </Tip>
                  }
                ></SideNavigation.Item>
              )}
            </>
          )}
        </SideNavigation.List>
      </SideNavigation>
      <ChatModeToggle
        open={showChatMode}
        closeHandler={() => setshowChatMode(false)}
        menuAnchor={chatModeAnchor}
      />
      {isChatModalOpen &&
        createPortal(
          <Dialog
            modalProps={{
              id: 'Chatbot-popup',
              className: 'n-p-token-4 n-rounded-lg h-[90%]',
            }}
            open={isChatModalOpen}
            size='unset'
            disableCloseButton={true}
          >
            <Dialog.Header className='flex justify-between self-end' id='chatbot-dialog-title'>
              <ExpandedChatButtonContainer
                closeChatBot={handleShrinkClick}
                deleteOnClick={deleteOnClick}
                messages={messages ?? []}
              />
            </Dialog.Header>
            <Dialog.Content className='flex flex-col n-gap-token-4 w-full grow overflow-auto'>
              <Chatbot
                isFullScreen={isFullScreen}
                clear={clearHistoryData}
                messages={messages ?? []}
                setMessages={setMessages}
                isLoading={getIsLoading(messages ?? [])}
              />
            </Dialog.Content>
          </Dialog>,
          document.body
        )}
    </div>
  );
};
export default SideNav;
