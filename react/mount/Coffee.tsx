import { debug } from 'console';
import React, { Suspense, useState, useEffect } from 'react';

const Coffee: React.FC<{ brew?: string|any, children: React.ReactNode }> = ({ brew, children, pass_children, ...props }) => {
    const FallbackComponent = () => <div> ☕ Brewing "{children}" ... </div>;
    const [GeneratedComponent, setGeneratedComponent] = useState<React.ComponentType<any>>(()=>FallbackComponent);
    const [loaded, setLoaded] = useState(false);
    brew = brew || "./__brew__.tsx"

    useEffect(() => {
        const loadComponent = async () => {
            if(loaded) return;
            console.log('loading component...')
            try {
                let Component: React.ReactNode = undefined;
                if(typeof brew === 'function') {
                    Component = brew;
                } else if(typeof brew === 'string') {
                    const module = await import(`${brew}`)
                    Component = module.default;
                }
                if(!Component) return;
                setLoaded(true);
                setGeneratedComponent(() => Component);
            } catch (error) {
                console.error('Failed to load component', error);
                setGeneratedComponent(() => FallbackComponent);
            }
        };
        // try loading component every 4s
        const interval = setInterval(loadComponent, 4*1000);
        return () => clearInterval(interval);
    }, [brew, loaded]);

    return (
        <Suspense fallback={<></>}>
            <GeneratedComponent {...props} children={pass_children}/>
        </Suspense>
    );
};

// export const withCoffee = (component) => ({coffee, children, ...props}) => {
//     useEffect(() => {
//         let rendered = component({children: children, ...props})
//         debugger
//         console.log({filename: rendered._source.fileName})
//     }, [])

//     return <Coffee brew={component} {...props} pass_children={children}>
//         {coffee}
//     </Coffee>
// };

export default Coffee;
