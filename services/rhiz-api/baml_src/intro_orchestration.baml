// Introduction Orchestration for Rhiz Protocol
// Generic introduction orchestration across any relationship graph
// Not specific to fundraising - works for any introduction use case

class MessageTone {
  formality string  // "formal" | "professional" | "casual" | "friendly"
  urgency string  // "high" | "medium" | "low"
  length string  // "brief" | "moderate" | "detailed"
}

class ContextHighlight {
  highlight string
  relevance_score int  // 0-100
  type string  // "shared_experience" | "mutual_connection" | "common_interest" | "complementary_skills"
}

class IntroductionMessage {
  recipient_did string
  recipient_name string
  subject_line string
  
  message_body string
  message_tone MessageTone
  
  context_highlights ContextHighlight[]
  call_to_action string
  
  optimal_send_time string  // ISO 8601 timestamp
  followup_timing_days int  // Days to wait before followup
  
  success_probability int  // 0-100, likelihood of positive response
  personalization_score int  // 0-100, how tailored the message is
}

function GenerateIntroRequest(
  requester_did: string,
  requester_context: string,  // Who is requesting and why
  intermediary_did: string,
  intermediary_context: string,  // Who is the intermediary
  target_did: string,
  target_context: string,  // Who is the target
  introduction_purpose: string,  // Why this introduction matters
  relationship_data: string  // JSON of relationship strengths and context
) -> IntroductionMessage {
  client GPT4
  prompt #"
    You are an expert at facilitating warm introductions through trust networks.
    
    Generate a personalized introduction request message.
    
    REQUESTER (Person asking for intro):
    DID: {{ requester_did }}
    Context: {{ requester_context }}
    
    INTERMEDIARY (Person making the intro):
    DID: {{ intermediary_did }}
    Context: {{ intermediary_context }}
    
    TARGET (Person to be introduced to):
    DID: {{ target_did }}
    Context: {{ target_context }}
    
    PURPOSE:
    {{ introduction_purpose }}
    
    RELATIONSHIP DATA:
    {{ relationship_data }}
    
    Craft a message that:
    1. Respects the intermediary's time and relationship capital
    2. Clearly states why this intro makes sense for all parties
    3. Makes it easy for intermediary to say yes (low-friction)
    4. Highlights mutual value (not extractive)
    5. Provides specific context, not generic requests
    6. Uses appropriate tone based on relationship formality
    
    Message should be:
    - Professional and respectful
    - Specific with relevant details
    - Clear on the ask
    - Highlighting mutual benefit where possible
    
    Include optimal timing for sending based on relationship context.
    
    Return structured JSON matching IntroductionMessage schema.
  "#
}

class ForwardingIntro {
  subject_line string
  intro_text string  // Text intermediary forwards to target
  
  requester_summary string  // Brief summary of requester
  value_proposition string  // Why target should care
  
  personalization_suggestions string[]  // Tips for intermediary to customize
  response_template string?  // Optional template if target says yes
}

function GenerateForwardingIntro(
  requester_context: string,
  target_context: string,
  intermediary_relationships: string,  // How intermediary knows both parties
  introduction_purpose: string,
  requested_outcome: string  // "meeting" | "email_intro" | "advice" | "collaboration"
) -> ForwardingIntro {
  client GPT4
  prompt #"
    Generate the forwarding introduction text that the intermediary sends to the target.
    
    REQUESTER: {{ requester_context }}
    TARGET: {{ target_context }}
    INTERMEDIARY'S RELATIONSHIPS: {{ intermediary_relationships }}
    PURPOSE: {{ introduction_purpose }}
    DESIRED OUTCOME: {{ requested_outcome }}
    
    Create text that the intermediary can forward, including:
    1. Why this intro makes sense (based on their relationships)
    2. Brief but compelling requester summary
    3. Clear value proposition for the target
    4. Specific ask (meeting, intro, advice, collaboration)
    5. Easy opt-out if not interested
    
    Make it easy for the intermediary - they should be able to use with minimal edits.
    
    Provide personalization suggestions so intermediary can add their own touch.
    
    Return structured JSON matching ForwardingIntro schema.
  "#
}

class FollowupMessage {
  message_body string
  subject_line string
  timing_justification string  // Why following up now
  new_information string?  // Any updates to mention
  tone_adjustment string  // How to adjust tone from original
}

function GenerateFollowup(
  original_message: string,
  days_since_sent: int,
  any_responses: bool,
  new_context: string?
) -> FollowupMessage {
  client GPT4Mini
  prompt #"
    Generate an appropriate followup message.
    
    ORIGINAL MESSAGE: {{ original_message }}
    DAYS SINCE SENT: {{ days_since_sent }}
    ANY RESPONSES: {{ any_responses }}
    {% if new_context %}
    NEW CONTEXT: {{ new_context }}
    {% endif %}
    
    Create a followup that:
    1. Acknowledges time passed
    2. Provides value or new information if possible
    3. Maintains professionalism without being pushy
    4. Makes it easy to respond
    5. Offers graceful out if not interested
    
    Adjust tone based on time elapsed:
    - 3-5 days: gentle reminder
    - 7-10 days: more direct, assume they're busy
    - 14+ days: assume low interest, soft close
    
    Return structured JSON matching FollowupMessage schema.
  "#
}

// Multi-step orchestration for complex intro paths (2+ hops)
class OrchestrationStep {
  step_number int
  recipient_did string
  message_type string  // "intro_request" | "forwarding_intro" | "followup" | "thank_you"
  message IntroductionMessage
  depends_on_step int?  // Which step must succeed first
  success_criteria string
}

class IntroOrchestrationPlan {
  total_steps int
  steps OrchestrationStep[]
  
  timeline_days int  // Expected time to complete
  success_probability int  // 0-100, overall probability
  
  risk_factors string[]
  mitigation_strategies string[]
  
  alternative_paths string[]  // Backup intro paths if this fails
}

function PlanIntroductionOrchestration(
  requester_did: string,
  target_did: string,
  intro_path: string,  // JSON array of DIDs in the path
  relationship_data: string,  // Trust scores and context for each hop
  introduction_purpose: string
) -> IntroOrchestrationPlan {
  client GPT4
  prompt #"
    Plan a multi-step introduction orchestration through a trust network.
    
    REQUESTER: {{ requester_did }}
    TARGET: {{ target_did }}
    INTRODUCTION PATH: {{ intro_path }}
    RELATIONSHIP DATA: {{ relationship_data }}
    PURPOSE: {{ introduction_purpose }}
    
    Create a step-by-step orchestration plan:
    
    For each person in the path:
    1. What message to send
    2. When to send it (relative timing)
    3. What success looks like
    4. What to do if they don't respond
    5. Dependencies (which steps must complete first)
    
    Consider:
    - Relationship strength at each hop
    - Optimal timing between steps
    - Risk factors (weak relationships, timing, complexity)
    - Backup paths if this fails
    
    Calculate realistic success probability based on:
    - Path strength (higher = better)
    - Number of hops (fewer = better)  
    - Relationship recency
    - Complexity of request
    
    Provide mitigation strategies for identified risks.
    
    Return structured JSON matching IntroOrchestrationPlan schema.
  "#
}

// Assess introduction feasibility before attempting
class IntroFeasibility {
  feasibility_score int  // 0-100, how feasible this intro is
  feasibility_level string  // "very_high" | "high" | "moderate" | "low" | "very_low"
  
  success_factors string[]
  blocking_factors string[]
  
  recommended_approach string
  timing_recommendation string  // "now" | "wait_for_context" | "not_recommended"
  
  alternative_suggestions string[]
}

function AssessIntroductionFeasibility(
  requester_did: string,
  target_did: string,
  proposed_path: string,  // JSON of the path
  relationship_data: string,
  introduction_purpose: string,
  timing_context: string?
) -> IntroFeasibility {
  client GPT4Mini
  prompt #"
    Assess the feasibility of this introduction before attempting it.
    
    REQUESTER: {{ requester_did }}
    TARGET: {{ target_did }}
    PROPOSED PATH: {{ proposed_path }}
    RELATIONSHIPS: {{ relationship_data }}
    PURPOSE: {{ introduction_purpose }}
    {% if timing_context %}
    TIMING CONTEXT: {{ timing_context }}
    {% endif %}
    
    Evaluate:
    1. Strength of relationships in the path
    2. Appropriateness of the request
    3. Timing considerations
    4. Potential obstacles
    5. Success factors
    
    Provide:
    - Overall feasibility score (0-100)
    - Success factors (what's working in your favor)
    - Blocking factors (what might prevent success)
    - Recommended approach
    - Timing recommendation (now vs. later vs. never)
    - Alternative suggestions if feasibility is low
    
    Be honest and realistic in assessment.
    
    Return structured JSON matching IntroFeasibility schema.
  "#
}

