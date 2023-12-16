import React, { ReactNode } from 'react';

// Define the props type for the Coffee component
export interface CoffeeProps {
    brew?: string | (() => JSX.Element);
    children: string;
    pass_children?: ReactNode;
}

// Declare the Coffee component with the specified props
declare const Coffee: React.FC<CoffeeProps>;
export default Coffee;
