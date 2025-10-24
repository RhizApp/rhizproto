/**
 * Opportunity Service - Discovers funding and growth opportunities for founders
 */

export interface Opportunity {
  id: string
  title: string
  type:
    | 'accelerator'
    | 'grant'
    | 'investor'
    | 'event'
    | 'competition'
    | 'community'
  description: string
  provider: string
  amount?: string
  deadline?: string
  location?: string
  stage: string[]
  url: string
  matchScore?: number
  tags: string[]
}

class OpportunityService {
  private opportunities: Opportunity[] = [
    // Accelerators
    {
      id: 'yc-w26',
      title: 'Y Combinator Winter 2026',
      type: 'accelerator',
      description:
        "The world's top startup accelerator. $500K investment for 7% equity. 3-month program in San Francisco.",
      provider: 'Y Combinator',
      amount: '$500K',
      deadline: 'December 1, 2025',
      location: 'San Francisco, CA',
      stage: ['pre-seed', 'seed'],
      url: 'https://www.ycombinator.com/apply',
      matchScore: 95,
      tags: ['equity', 'mentorship', 'network', 'demo-day'],
    },
    {
      id: 'techstars-2026',
      title: 'Techstars Accelerator Programs',
      type: 'accelerator',
      description:
        '120K investment + mentorship from successful founders and investors. Multiple city locations.',
      provider: 'Techstars',
      amount: '$120K',
      deadline: 'Rolling',
      location: 'Multiple Cities',
      stage: ['pre-seed', 'seed'],
      url: 'https://www.techstars.com/accelerators',
      matchScore: 88,
      tags: ['equity', 'mentorship', 'global', 'industry-specific'],
    },
    {
      id: 'on-deck-odf',
      title: 'On Deck Founders Fellowship',
      type: 'accelerator',
      description:
        '10-week program for early-stage founders. Access to 1000+ investors and operators.',
      provider: 'On Deck',
      amount: 'No equity',
      deadline: 'Rolling admissions',
      location: 'Remote',
      stage: ['idea', 'pre-seed'],
      url: 'https://www.beondeck.com/founders',
      matchScore: 82,
      tags: ['network', 'remote', 'community', 'no-equity'],
    },

    // Grants & Non-Dilutive Funding
    {
      id: 'stripe-climate',
      title: 'Stripe Climate Grants',
      type: 'grant',
      description:
        'Up to $1M for carbon removal and climate tech companies. No equity required.',
      provider: 'Stripe',
      amount: 'Up to $1M',
      deadline: 'Quarterly reviews',
      location: 'Global',
      stage: ['seed', 'series-a'],
      url: 'https://stripe.com/climate',
      matchScore: 75,
      tags: ['climate', 'non-dilutive', 'carbon-removal', 'impact'],
    },
    {
      id: 'aws-activate',
      title: 'AWS Activate',
      type: 'grant',
      description:
        'Up to $100K in AWS credits plus technical support and training.',
      provider: 'Amazon Web Services',
      amount: 'Up to $100K credits',
      deadline: 'Rolling',
      location: 'Global',
      stage: ['pre-seed', 'seed', 'series-a'],
      url: 'https://aws.amazon.com/activate',
      matchScore: 92,
      tags: ['credits', 'infrastructure', 'non-dilutive', 'saas'],
    },
    {
      id: 'sbir-grants',
      title: 'SBIR/STTR Grants',
      type: 'grant',
      description:
        'US government grants for R&D. Phase I: $250K, Phase II: $1-2M. Non-dilutive.',
      provider: 'US Government',
      amount: '$250K - $2M',
      deadline: 'Multiple cycles/year',
      location: 'United States',
      stage: ['pre-seed', 'seed', 'series-a'],
      url: 'https://www.sbir.gov',
      matchScore: 78,
      tags: ['non-dilutive', 'r&d', 'government', 'deep-tech'],
    },

    // Investors & VCs
    {
      id: 'sequoia-arc',
      title: 'Sequoia Capital ARC Program',
      type: 'investor',
      description:
        "Company-building program with access to Sequoia's network before formal investment.",
      provider: 'Sequoia Capital',
      amount: 'Varies',
      deadline: 'Rolling applications',
      location: 'San Francisco, CA',
      stage: ['pre-seed', 'seed'],
      url: 'https://www.sequoiacap.com/arc',
      matchScore: 85,
      tags: ['top-tier', 'network', 'resources', 'workshop'],
    },
    {
      id: 'a16z-crypto',
      title: 'a16z Crypto Startup School',
      type: 'investor',
      description:
        '12-week program for crypto founders. Free to attend, no equity required.',
      provider: 'Andreessen Horowitz',
      amount: 'No cost',
      deadline: 'Annual cohorts',
      location: 'Remote',
      stage: ['idea', 'pre-seed'],
      url: 'https://a16zcrypto.com/crypto-startup-school',
      matchScore: 80,
      tags: ['crypto', 'web3', 'education', 'no-equity'],
    },

    // Competitions
    {
      id: 'techcrunch-battlefield',
      title: 'TechCrunch Disrupt Battlefield',
      type: 'competition',
      description:
        'Startup competition at TechCrunch Disrupt. $100K prize + exposure to press and investors.',
      provider: 'TechCrunch',
      amount: '$100K prize',
      deadline: 'August 2026',
      location: 'San Francisco, CA',
      stage: ['pre-seed', 'seed'],
      url: 'https://techcrunch.com/startup-battlefield',
      matchScore: 72,
      tags: ['competition', 'exposure', 'press', 'networking'],
    },
    {
      id: 'mit-prize',
      title: 'MIT $100K Entrepreneurship Competition',
      type: 'competition',
      description:
        'One of the most prestigious student startup competitions. $100K in prizes.',
      provider: 'MIT',
      amount: '$100K',
      deadline: 'Spring 2026',
      location: 'Cambridge, MA',
      stage: ['idea', 'pre-seed'],
      url: 'https://www.mit100k.org',
      matchScore: 68,
      tags: ['competition', 'student', 'prizes', 'prestige'],
    },

    // Events & Networking
    {
      id: 'saastr-annual',
      title: 'SaaStr Annual 2026',
      type: 'event',
      description:
        "World's largest B2B SaaS conference. Connect with 12,000+ founders and investors.",
      provider: 'SaaStr',
      amount: '$1,500 - $3,000',
      deadline: 'September 2026',
      location: 'San Francisco, CA',
      stage: ['seed', 'series-a', 'series-b'],
      url: 'https://www.saastr.com/annual',
      matchScore: 70,
      tags: ['conference', 'saas', 'networking', 'b2b'],
    },
    {
      id: 'collision-conf',
      title: 'Collision Conference 2026',
      type: 'event',
      description:
        "America's fastest-growing tech conference. 35,000+ attendees, startup exhibition.",
      provider: 'Web Summit',
      amount: '$995 - $2,995',
      deadline: 'June 2026',
      location: 'Toronto, Canada',
      stage: ['pre-seed', 'seed', 'series-a'],
      url: 'https://collisionconf.com',
      matchScore: 76,
      tags: ['conference', 'exhibition', 'press', 'investors'],
    },

    // Communities
    {
      id: 'indie-hackers',
      title: 'Indie Hackers Community',
      type: 'community',
      description:
        'Community of founders building profitable online businesses. Free to join.',
      provider: 'Indie Hackers',
      amount: 'Free',
      deadline: 'Open',
      location: 'Online',
      stage: ['idea', 'pre-seed', 'seed'],
      url: 'https://www.indiehackers.com',
      matchScore: 84,
      tags: ['community', 'bootstrapping', 'peer-support', 'learning'],
    },
    {
      id: 'first-round-network',
      title: 'First Round Network',
      type: 'community',
      description:
        'Exclusive community for First Round-backed founders. Resources, events, connections.',
      provider: 'First Round Capital',
      amount: 'Members only',
      deadline: 'Portfolio companies',
      location: 'San Francisco / New York',
      stage: ['seed', 'series-a'],
      url: 'https://firstround.com/companies',
      matchScore: 65,
      tags: ['community', 'portfolio', 'exclusive', 'resources'],
    },
  ]

  private async fetchWithAuth(
    _url: string,
    _options: RequestInit = {},
  ): Promise<Response> {
    // For now, this is a mock service - no actual fetch needed
    // In production, this would call a real API
    return new Response(JSON.stringify(this.opportunities), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  async discoverOpportunities(filters?: {
    type?: Opportunity['type']
    stage?: string
    tags?: string[]
    minMatchScore?: number
  }): Promise<Opportunity[]> {
    let filtered = [...this.opportunities]

    if (filters) {
      if (filters.type) {
        filtered = filtered.filter((opp) => opp.type === filters.type)
      }
      if (filters.stage) {
        filtered = filtered.filter((opp) => opp.stage.includes(filters.stage!))
      }
      if (filters.tags && filters.tags.length > 0) {
        filtered = filtered.filter((opp) =>
          filters.tags!.some((tag) => opp.tags.includes(tag)),
        )
      }
      if (filters.minMatchScore) {
        filtered = filtered.filter(
          (opp) => (opp.matchScore || 0) >= filters.minMatchScore!,
        )
      }
    }

    // Sort by match score descending
    filtered.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))

    return filtered
  }

  async getOpportunity(id: string): Promise<Opportunity | null> {
    return this.opportunities.find((opp) => opp.id === id) || null
  }

  async getTopOpportunities(limit = 5): Promise<Opportunity[]> {
    return [...this.opportunities]
      .sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0))
      .slice(0, limit)
  }
}

export const opportunityService = new OpportunityService()
