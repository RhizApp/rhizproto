/**
 * Cryptographic Signing for Relationship Records
 * All relationship records must be signed by both participants
 */

import { Secp256k1Keypair } from '@atproto/crypto'
import { cidForCbor, TID } from '@atproto/common'

/**
 * Signature data for a relationship record
 */
export interface RelationshipSignature {
  did: string
  signature: string // Base64-encoded
  signedAt: string // ISO8601 timestamp
}

/**
 * Signable relationship data
 * This is what gets hashed and signed
 */
export interface SignableRelationshipData {
  participants: [string, string]
  type: string
  strength: number
  context: string
  createdAt: string
}

/**
 * Sign relationship data with a keypair
 */
export async function signRelationship(
  data: SignableRelationshipData,
  keypair: Secp256k1Keypair,
  did: string,
): Promise<RelationshipSignature> {
  // Create canonical representation
  const canonical = JSON.stringify(data, Object.keys(data).sort())
  const bytes = new TextEncoder().encode(canonical)

  // Sign the data
  const signature = await keypair.sign(bytes)

  return {
    did,
    signature: Buffer.from(signature).toString('base64'),
    signedAt: new Date().toISOString(),
  }
}

/**
 * Verify a relationship signature
 */
export async function verifyRelationshipSignature(
  data: SignableRelationshipData,
  signature: RelationshipSignature,
  publicKey: string,
): Promise<boolean> {
  try {
    // Reconstruct canonical representation
    const canonical = JSON.stringify(data, Object.keys(data).sort())
    const bytes = new TextEncoder().encode(canonical)

    // Decode signature
    const sigBytes = Buffer.from(signature.signature, 'base64')

    // Verify using the public key
    // Note: In production, this would use the actual verification logic
    // from @atproto/crypto with the signing key from the DID document
    return true // Placeholder - implement full verification
  } catch {
    return false
  }
}

/**
 * Verify that a relationship has valid signatures from both participants
 */
export async function verifyRelationshipSignatures(
  data: SignableRelationshipData,
  signatures: RelationshipSignature[],
  publicKeys: Map<string, string>,
): Promise<boolean> {
  // Must have exactly 2 signatures, one from each participant
  if (signatures.length !== 2) {
    return false
  }

  // Verify each participant signed
  const signingDids = new Set(signatures.map((s) => s.did))
  if (
    !signingDids.has(data.participants[0]) ||
    !signingDids.has(data.participants[1])
  ) {
    return false
  }

  // Verify each signature
  for (const sig of signatures) {
    const publicKey = publicKeys.get(sig.did)
    if (!publicKey) {
      return false
    }

    const isValid = await verifyRelationshipSignature(data, sig, publicKey)
    if (!isValid) {
      return false
    }
  }

  return true
}

/**
 * Generate a TID (Timestamp ID) for a new relationship record
 */
export function generateRelationshipTid(): string {
  return TID.nextStr()
}

