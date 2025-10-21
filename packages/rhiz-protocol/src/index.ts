/**
 * @rhiz/protocol
 * Core protocol schemas, types, and validators for Rhiz Protocol
 */

// Export legacy types (will be deprecated after migration)
export * from './types';
export * from './validators';

// Export constants
export * from './constants';

// Export AT Protocol native modules
export * from './identity';
export * from './signing';
export * from './repo';

// Export generated types (after codegen runs)
export * from './generated';

// Version
export const PROTOCOL_VERSION = '0.1.0';

