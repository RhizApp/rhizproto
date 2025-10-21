/**
 * AT Protocol Identity Integration
 * DID resolution and identity verification for Rhiz Protocol
 */

import { AtprotoIdentityResolver } from '@atproto-labs/identity-resolver'
import { DidPlcResolver, DidWebResolver } from '@atproto-labs/did-resolver'
import { HandleResolverNodejs } from '@atproto-labs/handle-resolver-node'

/**
 * Resolved identity information for an entity
 */
export interface ResolvedIdentity {
  did: string
  handle?: string
  pds?: string
  signingKey?: string
}

/**
 * Identity resolver for Rhiz Protocol entities
 * Resolves DIDs and handles to full identity information
 */
export class RhizIdentityResolver {
  private resolver: AtprotoIdentityResolver

  constructor() {
    // Initialize with PLC and Web DID resolvers
    const didResolver = new DidPlcResolver()
    const didWebResolver = new DidWebResolver()
    const handleResolver = new HandleResolverNodejs()

    // Combine resolvers
    const combinedResolver = {
      async resolve(did: string) {
        if (did.startsWith('did:plc:')) {
          return didResolver.resolve(did)
        } else if (did.startsWith('did:web:')) {
          return didWebResolver.resolve(did)
        }
        throw new Error(`Unsupported DID method: ${did}`)
      },
    }

    this.resolver = new AtprotoIdentityResolver(combinedResolver as any, handleResolver)
  }

  /**
   * Resolve a DID or handle to full identity information
   */
  async resolve(didOrHandle: string): Promise<ResolvedIdentity> {
    const identity = await this.resolver.resolve(didOrHandle)

    return {
      did: identity.did,
      handle: identity.handle,
      pds: identity.pds,
      signingKey: identity.signingKey,
    }
  }

  /**
   * Resolve a handle to its DID
   */
  async resolveDid(handle: string): Promise<string> {
    const identity = await this.resolve(handle)
    return identity.did
  }

  /**
   * Resolve a DID to its handle (if available)
   */
  async resolveHandle(did: string): Promise<string | undefined> {
    const identity = await this.resolve(did)
    return identity.handle
  }

  /**
   * Validate that a DID is properly formatted and resolvable
   */
  async validate(did: string): Promise<boolean> {
    try {
      await this.resolve(did)
      return true
    } catch {
      return false
    }
  }
}

// Export singleton instance
export const identityResolver = new RhizIdentityResolver()

