import { Box, Dialog, Tabs, Typography } from '@neo4j-ndl/react';
import weblogo from '../../assets/images/web.svg';
import webdarkmode from '../../assets/images/web-darkmode.svg';
import { useContext, useState } from 'react';
import WebInput from './Web/WebInput';
import { APP_SOURCES } from '../../utils/Constants';
import Neo4jDataImportFromCloud from '../../assets/images/data-from-cloud.svg';
import { ThemeWrapperContext } from '../../context/ThemeWrapper';

/* GenericModal 组件是一个通用的弹窗组件，用于展示不同来源（Web等）的输入界面 */
export default function GenericModal({
  open,
  closeHandler,
  isOnlyWeb,
}: {
  open: boolean;
  closeHandler: () => void;
  isOnlyWeb?: boolean;
}) {
  const themeUtils = useContext(ThemeWrapperContext);
  const [activeTab, setactiveTab] = useState<number>(isOnlyWeb ? 0 : 0);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  return (
    <Dialog open={open} onClose={closeHandler}>
      <Dialog.Header>
        <Box className='flex flex-row pb-6 items-center mb-2'>
          <img src={Neo4jDataImportFromCloud} style={{ width: 95, height: 95, marginRight: 10 }} loading='lazy' />
          <Box className='flex flex-col'>
            <Typography variant='h2'>Web Sources</Typography>
            <Typography variant='body-medium' className='mb-2'>
              Convert Any Web Source to Knowledge graph
            </Typography>
          </Box>
        </Box>
        <Tabs fill='underline' onChange={setactiveTab} size='large' value={activeTab}>
          {/* {APP_SOURCES != undefined && APP_SOURCES.includes('youtube') && (
            <Tabs.Tab tabId={0} aria-label='Database' disabled={isLoading}>
              <img
                src={themeUtils.colorMode === 'light' ? youtubelightmodelogo : youtubedarkmodelogo}
                className={`brandimg`}
              ></img>
            </Tabs.Tab>
          )}
          {APP_SOURCES != undefined && APP_SOURCES.includes('wiki') && (
            <Tabs.Tab tabId={1} aria-label='Add database' disabled={isLoading}>
              <img
                src={themeUtils.colorMode === 'dark' ? wikipedialogo : wikipediadarkmode}
                className={`brandimg`}
              ></img>
            </Tabs.Tab>
          )} */}
          {APP_SOURCES != undefined && APP_SOURCES.includes('web') && (
            <Tabs.Tab tabId={0} aria-label='Inbox' disabled={isLoading}>
              <img src={themeUtils.colorMode === 'dark' ? webdarkmode : weblogo} className={`brandimg`}></img>
            </Tabs.Tab>
          )}
        </Tabs>
        {/* {APP_SOURCES != undefined && APP_SOURCES.includes('youtube') && (
          <Tabs.TabPanel className='n-flex n-flex-col n-gap-token-4 n-p-token-6' value={activeTab} tabId={0}>
            <YoutubeInput setIsLoading={setIsLoading} />
          </Tabs.TabPanel>
        )}
        {APP_SOURCES != undefined && APP_SOURCES.includes('wiki') && (
          <Tabs.TabPanel className='n-flex n-flex-col n-gap-token-4 n-p-token-6' value={activeTab} tabId={1}>
            <WikipediaInput setIsLoading={setIsLoading} />
          </Tabs.TabPanel>
        )} */}
        {APP_SOURCES != undefined && APP_SOURCES.includes('web') && (
          <Tabs.TabPanel className='n-flex n-flex-col n-gap-token-4 n-p-token-6' value={activeTab} tabId={0}>
            <WebInput setIsLoading={setIsLoading} />
          </Tabs.TabPanel>
        )}
      </Dialog.Header>
    </Dialog>
  );
}
