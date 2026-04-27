"""
Response Synthesizer
Combines results from multiple agents into coherent responses.
"""

from typing import List, Dict, Any, Optional


class ResponseSynthesizer:
    """
    Synthesizes responses from multiple agents into a unified answer.
    """
    
    def __init__(self, model_layer=None):
        """
        Initialize synthesizer.
        
        Args:
            model_layer: Optional ModelLayer for LLM-based synthesis
        """
        self.model = model_layer
    
    async def synthesize(
        self,
        query: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize agent results into final response.
        
        Args:
            query: Original user query
            execution_result: Results from AgentExecutor
            
        Returns:
            Synthesized response
        """
        results = execution_result.get("results", [])
        strategy = execution_result.get("strategy", "single")
        
        # Filter successful results
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            # Include error details for debugging
            error_details = []
            for r in results:
                agent_name = r.get("agent", "Unknown")
                error = r.get("error", "Unknown error")
                error_details.append(f"{agent_name}: {error}")
            
            error_message = "I apologize, but I encountered errors processing your request. Please try again."
            if error_details:
                error_message += f"\n\nDebug info: {'; '.join(error_details)}"
            
            return {
                "response": error_message,
                "success": False,
                "agent_responses": results
            }
        
        # Synthesize based on strategy
        if strategy == "single":
            return await self._synthesize_single(query, successful_results[0])
        elif len(successful_results) == 1:
            return await self._synthesize_single(query, successful_results[0])
        else:
            return await self._synthesize_multiple(query, successful_results)
    
    async def _synthesize_single(
        self,
        query: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize single agent response"""
        return {
            "response": result.get("response", ""),
            "agent": result.get("agent", ""),
            "success": True,
            "sources": [result]
        }
    
    async def _synthesize_multiple(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize multiple agent responses"""
        if self.model:
            return await self._synthesize_with_llm(query, results)
        else:
            return self._synthesize_rule_based(query, results)
    
    async def _synthesize_with_llm(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to synthesize responses"""
        # Format agent responses
        agent_responses = []
        for result in results:
            agent_name = result.get("agent", "Unknown")
            response = result.get("response", "")
            agent_responses.append(f"**{agent_name.title()} Agent:**\n{response}")
        
        responses_text = "\n\n".join(agent_responses)
        
        # Create synthesis prompt
        prompt = f"""Synthesize these agent responses into a coherent, comprehensive answer.

User Query: {query}

Agent Responses:
{responses_text}

Create a unified response that:
1. Addresses the user's query directly
2. Integrates insights from all agents
3. Highlights key recommendations
4. Maintains a helpful, professional tone
5. Is concise but complete

Synthesized Response:"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a financial advisor synthesizing expert opinions."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.model.generate(
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                "response": response["content"],
                "success": True,
                "sources": results,
                "synthesis_method": "llm"
            }
        except Exception as e:
            # Fall back to rule-based
            return self._synthesize_rule_based(query, results)
    
    def _synthesize_rule_based(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Rule-based synthesis without LLM"""
        # Create structured response
        response_parts = []
        
        # Add introduction
        agent_names = [r.get("agent", "").title() for r in results]
        response_parts.append(
            f"Based on analysis from {', '.join(agent_names)}, here's what I found:\n"
        )
        
        # Add each agent's response
        for result in results:
            agent_name = result.get("agent", "Unknown").title()
            response = result.get("response", "")
            
            response_parts.append(f"\n**{agent_name} Analysis:**")
            response_parts.append(response)
        
        # Add summary
        response_parts.append("\n**Summary:**")
        response_parts.append(self._generate_summary(results))
        
        return {
            "response": "\n".join(response_parts),
            "success": True,
            "sources": results,
            "synthesis_method": "rule_based"
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate summary from multiple results"""
        # Extract key points
        key_points = []
        
        for result in results:
            agent = result.get("agent", "").title()
            response = result.get("response", "")
            
            # Extract first sentence as key point
            sentences = response.split(". ")
            if sentences:
                key_points.append(f"- {agent}: {sentences[0]}")
        
        return "\n".join(key_points)
    
    def rank_responses(
        self,
        results: List[Dict[str, Any]],
        criteria: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Rank agent responses by criteria.
        
        Args:
            results: List of agent results
            criteria: Ranking criteria (relevance, confidence, length)
            
        Returns:
            Ranked results
        """
        if criteria == "length":
            # Rank by response length (longer = more detailed)
            return sorted(
                results,
                key=lambda r: len(r.get("response", "")),
                reverse=True
            )
        elif criteria == "confidence":
            # Rank by confidence score if available
            return sorted(
                results,
                key=lambda r: r.get("confidence", 0.5),
                reverse=True
            )
        else:
            # Default: maintain original order (relevance from planner)
            return results
    
    def extract_recommendations(
        self,
        results: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract actionable recommendations from results.
        
        Args:
            results: List of agent results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for result in results:
            response = result.get("response", "")
            
            # Look for recommendation patterns
            lines = response.split("\n")
            for line in lines:
                line = line.strip()
                # Check for recommendation indicators
                if any(indicator in line.lower() for indicator in [
                    "recommend", "suggest", "should", "consider", "try", "action"
                ]):
                    if line and not line.startswith("#"):
                        recommendations.append(line)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def detect_conflicts(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicting recommendations from agents.
        
        Args:
            results: List of agent results
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Simple conflict detection based on keywords
        positive_keywords = ["increase", "more", "higher", "add", "expand"]
        negative_keywords = ["decrease", "less", "lower", "reduce", "cut"]
        
        for i, result1 in enumerate(results):
            for result2 in results[i+1:]:
                response1 = result1.get("response", "").lower()
                response2 = result2.get("response", "").lower()
                
                # Check for opposite recommendations
                has_positive1 = any(kw in response1 for kw in positive_keywords)
                has_negative1 = any(kw in response1 for kw in negative_keywords)
                has_positive2 = any(kw in response2 for kw in positive_keywords)
                has_negative2 = any(kw in response2 for kw in negative_keywords)
                
                if (has_positive1 and has_negative2) or (has_negative1 and has_positive2):
                    conflicts.append({
                        "agent1": result1.get("agent"),
                        "agent2": result2.get("agent"),
                        "type": "opposite_recommendations"
                    })
        
        return conflicts
