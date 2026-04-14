import { webLinkValidation } from '../../../utils/Utils';
import useSourceInput from '../../../hooks/useSourceInput';
import CustomSourceInput from '../CustomSourceInput';

/* WebInput 组件用于处理用户输入的网页链接，提供验证、状态管理和交互功能 */
// 内置链接验证逻辑（webLinkValidation），保证输入格式合法
// 使用自定义 Hook（useSourceInput）管理输入状态、验证结果、交互逻辑等，简化组件代码
// 组件入参：setIsLoading 用于控制父组件的加载状态，提升用户体验
export default function WebInput({ setIsLoading }: { setIsLoading: React.Dispatch<React.SetStateAction<boolean>> }) {
  const {
    inputVal,
    onChangeHandler,
    onBlurHandler,
    submitHandler,
    status,
    setStatus,
    statusMessage,
    isFocused,
    isValid,
    onClose,
    onPasteHandler,
  } = useSourceInput(webLinkValidation, setIsLoading, 'web-url', false, false, true);
  return (
    <CustomSourceInput
      onCloseHandler={onClose}
      isFocused={isFocused}
      isValid={isValid}
      disabledCheck={false}
      label='Website Link'
      placeHolder='https://baike.baidu.com/item/故障诊断'
      value={inputVal}
      onChangeHandler={onChangeHandler}
      onBlurHandler={onBlurHandler}
      submitHandler={submitHandler}
      setStatus={setStatus}
      status={status}
      statusMessage={statusMessage}
      id='Website link'
      onPasteHandler={onPasteHandler}
    />
  );
}
