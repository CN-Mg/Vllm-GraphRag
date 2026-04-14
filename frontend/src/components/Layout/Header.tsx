import Neo4jLogoBW from '../../logo.svg';
import Neo4jLogoColor from '../../logo-color.svg';
import {
  MoonIconOutline,
  SunIconOutline,
  CodeBracketSquareIconOutline,
  InformationCircleIconOutline,
} from '@neo4j-ndl/react/icons';
import { Typography } from '@neo4j-ndl/react';
import { useCallback, useEffect } from 'react';
import IconButtonWithToolTip from '../UI/IconButtonToolTip';
import { tooltips } from '../../utils/Constants';
import { useFileContext } from '../../context/UsersFiles';

export default function Header({ themeMode, toggleTheme }: { themeMode: string; toggleTheme: () => void }) {
  const handleURLClick = useCallback((url: string) => {
    window.open(url, '_blank');
  }, []);

  const { isSchema, setIsSchema } = useFileContext();

  useEffect(() => {
    setIsSchema(isSchema);
  }, [isSchema]);

  return (
    <div
      className='n-bg-palette-neutral-bg-weak p-1'
      style={{ borderBottom: '2px solid rgb(var(--theme-palette-neutral-border-weak))' }}
    >
      <nav
        className='flex items-center justify-between flex-row'
        role='navigation'
        data-testid='navigation'
        id='navigation'
        aria-label='main navigation'
      >
        {}
        <section className='flex w-5/6 shrink-0 grow-0 items-center justify-center min-w-[200px]'> 
          <Typography variant='h6' component='a' href='#app-bar-with-responsive-menu' className='flex items-center gap-3 no-underline'>
            <img
              src={themeMode === 'dark' ? Neo4jLogoBW : Neo4jLogoColor}
              className='h-8 min-h-8 min-w-8'
              alt='Neo4j Logo'
            />
            <span 
              className='text-lg font-semibold whitespace-nowrap'
              style={{ 
                color: themeMode === 'dark' ? '#fff' : '#000'
              }}
            >
              LLM-Graph for Fault Diagnosis
            </span>
          </Typography>
        </section>

        {}
        <section className='items-center justify-end w-1/3 grow-0 flex'>
          <div>
            <div
              className='inline-flex gap-x-1'
              style={{ display: 'flex', flexGrow: 0, alignItems: 'center', gap: '4px' }}
            >
              <IconButtonWithToolTip
                text={tooltips.documentation}
                onClick={() => handleURLClick('https://neo4j.com/docs/getting-started/')}
                size='large'
                clean
                placement='left'
                label={tooltips.documentation}
              >
                <InformationCircleIconOutline className='n-size-token-7' />
              </IconButtonWithToolTip>

              <IconButtonWithToolTip
                label={tooltips.github}
                onClick={() => handleURLClick('https://github.com/CN-Mg')}
                text={tooltips.github}
                size='large'
                clean
              >
                <CodeBracketSquareIconOutline />
              </IconButtonWithToolTip>

              <IconButtonWithToolTip
                label={tooltips.theme}
                text={tooltips.theme}
                clean
                size='large'
                onClick={toggleTheme}
                placement='left'
              >
                {themeMode === 'dark' ? (
                  <SunIconOutline />
                ) : (
                  <MoonIconOutline />
                )}
              </IconButtonWithToolTip>
            </div>
          </div>
        </section>
      </nav>
    </div>
  );
}