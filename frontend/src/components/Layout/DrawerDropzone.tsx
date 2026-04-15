import { Drawer, Flex, StatusIndicator, Typography } from '@neo4j-ndl/react';
import DropZone from '../DataSources/Local/DropZone';
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { healthStatus } from '../../services/HealthStatus';
import { DrawerProps } from '../../types';
import CustomAlert from '../UI/Alert';
import { useAlertContext } from '../../context/Alert';
import { APP_SOURCES } from '../../utils/Constants';
import GenericButton from '../WebSources/GenericSourceButton';
import GenericModal from '../WebSources/GenericSourceModal';

/* DrawerDropzone 组件是侧边栏中的一个核心组件，负责根据环境变量动态渲染不同的数据源输入选项（本地文件、Web来源等），并显示后端连接状态 */
const DrawerDropzone: React.FC<DrawerProps> = ({ isExpanded }) => {
  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  const [showGenericModal, setshowGenericModal] = useState<boolean>(false);
  const { closeAlert, alertState } = useAlertContext();

  useEffect(() => {
    async function getHealthStatus() {
      try {
        const response = await healthStatus();
        setIsBackendConnected(response.data.healthy);
      } catch (error) {
        setIsBackendConnected(false);
      }
    }
    getHealthStatus();
  }, []);

  const openGenericModal = useCallback(() => {
    setshowGenericModal(true);
  }, []);
  const closeGenericModal = useCallback(() => {
    setshowGenericModal(false);
  }, []);

  // 仅保留Web的判断（删除Youtube/Wiki相关）
  const iswebOnlyCheck = useMemo(
    () => APP_SOURCES?.includes('web'),
    [APP_SOURCES]
  );

  return (
    <div className='flex min-h-[calc(-58px+100vh)] relative'>
      <Drawer expanded={isExpanded} position='left' type='push' closeable={false}>
        <Drawer.Body className={`!overflow-hidden !w-[294px]`} style={{ height: 'intial' }}>
          {alertState.showAlert && (
            <CustomAlert
              severity={alertState.alertType}
              open={alertState.showAlert}
              handleClose={closeAlert}
              alertMessage={alertState.alertMessage}
            />
          )}
          <div className='flex h-full flex-col'>
            <div className='relative h-full'>
              <div className='flex flex-col h-full'>
                <div
                  className={`mx-6 flex flex-none items-center justify-between ${
                    process.env.ENV != 'PROD' ? 'pb-6' : 'pb-5' // 根据环境调整底部padding，DEV环境增加间距显示后端状态，PROD环境减少间距
                  }`}
                >
                  {process.env.ENV != 'PROD' && (
                    <Typography variant='body-medium' className='flex items-center content-center'>
                      <Typography variant='body-medium'>
                        {!isBackendConnected ? <StatusIndicator type='danger' /> : <StatusIndicator type='success' />}
                      </Typography>
                      <span>Backend connection status</span>
                    </Typography>
                  )}
                </div>
                {process.env.ENV != 'PROD' ? (
                  <>
                    <Flex gap='6' className='h-full source-container'>
                      {/* Local 文件上传 */}
                      {APP_SOURCES != undefined && APP_SOURCES.includes('local') && (
                        <div className='px-6 outline-dashed outline-2 outline-offset-2 outline-gray-100 imageBg'>
                          <DropZone />
                        </div>
                      )}
                      {/* Web 组件独立渲染 */}
                      {APP_SOURCES != undefined && APP_SOURCES.includes('web') && (
                        <div className={`outline-dashed imageBg ${process.env.ENV === 'PROD' ? 'w-[245px]' : ''}`}>
                          <GenericButton openModal={openGenericModal}></GenericButton>
                          <GenericModal
                            isOnlyWeb={iswebOnlyCheck}
                            open={showGenericModal}
                            closeHandler={closeGenericModal}
                          ></GenericModal>
                        </div>
                      )}
                    </Flex>
                  </>
                ) : (
                  <>
                    <Flex gap='6' className='h-full source-container'>
                      {/* Local 文件上传 */}
                      {APP_SOURCES != undefined && APP_SOURCES.includes('local') && (
                        <div className='px-6 outline-dashed outline-2 outline-offset-2 outline-gray-100 imageBg'>
                          <DropZone />
                        </div>
                      )}
                      {/* Web 组件独立渲染 */}
                      {APP_SOURCES != undefined && APP_SOURCES.includes('web') && (
                        <div className={`outline-dashed imageBg ${process.env.ENV === 'PROD' ? 'w-[245px]' : ''}`}>
                          <GenericButton openModal={openGenericModal}></GenericButton>
                          <GenericModal
                            isOnlyWeb={iswebOnlyCheck}
                            open={showGenericModal}
                            closeHandler={closeGenericModal}
                          ></GenericModal>
                        </div>
                      )}
                    </Flex>
                  </>
                )}
              </div>
            </div>
          </div>
        </Drawer.Body>
      </Drawer>
    </div>
  );
};

export default DrawerDropzone;
