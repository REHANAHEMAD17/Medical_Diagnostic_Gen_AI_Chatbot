import json
import os
import uuid
import datetime import datetime
import openai 
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class ReportQASystem:

    def __init__(self_api_key= None):

        self.api_key= api_key
        self.conversation_history=[]
        self.analysis_store= self.load_analysis_store()

    def load_analysis_store(self):
        """Load the analysis store from disk"""
        if os.path.exist("analysis_store.json"):
            with open ("analysis_store.json", "r") as f:
                return json.load(f)
        return {"analyses": []}
    
    def get_embeddings(self, text, model= "text-embedding-ada-002"):
        """Get embeddings for text using OpenAI"""
        if not self.api_key:
            return np.random.rand(1536)
        
        try:
            client= openai.OpenAI(api_key= self.api_key)
            response= client.embeddings.create(
                input= text,
                model= model
            )

            return response.data[0].embedding
        
        except Exception as e:
            print(f" Error getting embeddings: {e}")
            #Return dummy embedding on error (showing)
            return np.random.rand(1536)
        

    def get_relavant_contexts(self, query, top_k= 3):
        """find the relevant contexts for a query using embeddings similarity"""

        # Get query embeddings
        query_embedding= self.get_embeddings(query)

        #Extract all analyses and get embeddings
        analyses= self.analyis_store["analyses"]
        contexts= []

        # Get embeddings for each analysis
        for analysis in analysis:
            analysis_text= analysis.get("analysis", "")
            if not analysis_text.strip():
                continue

            # Combine the analysis with findings
            full_text= analysis_text
            if "findings" in analysis and analysis["findings"]:
                findings_text ="\n".join([f"- {finding}" for finding in analysis["findings"]])
                full_text += f"\n\nFindings: \n{findings_text}"


            # Add metadata
            full_text= f"\n\nImage: {analysis.get('filename', 'unknown')}"
            full_text= f"\nDate: {analysis.get('date', '')[:10]}"

            contexts.append({
                "text": full_text,
                "embedding": self.get_embeddings(full_text),
                "id": analysis.get("id", ""),
                "date": analysis.get("date","")
                    })
            
        #calculate similarities
        similarities= []
        for context in contexts:
            similarity =cosine_similarity([query_embedding], [context["embedding"]])[0][0]
            similarities.append((similarity, context))


        # Sort by similarity and get top_k
        similarities.sort(reverse= True)
        top_contexts =[context["text"] for_, context in similarities[:top_k]]

        return top_contexts
    
    def answer_question(self, question):
        try:
            # Write here code reming
            response= client.chat.completions.create(
                model= "gpt-3.5-turbo",
                messages= messages,
                max_tokens= 500, 
                temperature= 0.3
            )

            answer= response.choices[0].message.content

            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Keep conversation history managable
            if len(self.conversation_history)> 10:
                self.conversation_history= self.conversation_history[-10:]

            return answer

        except Exception as e:
            return f"I encountered and error while answering your question: {str(e)}"
    

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history= []
        return "Conversation.history cleared."
    


class ReportQAChat:       #>>>>>for storing data
    def __init__(self):
        self.qa_chat_store= self.get_qa_chat_store()


    def get_qa_chat_store(self):
        """Get the QA chat storage"""
        if os.path.exists("qa_chat_store.json"):
            with open("qa_chat_store.json", "r") as f:
                return json.load(f)
        return {"rooms": {}}
    
    def save_qa_chat_store(self):
        """Save the QA Chat storeage"""
        with open("qa_chat_store.json", "w") as f:
            json.dump(self.qa_chat_store, f)


    def create_qa_room(self, user_name, room_name):
        """Create a new QA chat room"""

        room_id = f"QA-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        room_data= {
            "id": room_id, 
            "name": room_name,
            "created_at": datetime.now().isoformat(),
            "creator": user_name,
            "messages": []
        }

        welcome_message= {
            "id": str(uuid.uuid4()),
            "user": "Report QA System",
            "content": f"Welcomes to the Report QA room: {room_name}. You can ask questions about your medical reports and I will try to answer based on the analyses stored in the system."",
            "timestamp": datetime.now().isoformat() 
        }

        room_data["messages"].append(welcome_message)

        #Store room
        self.qa_chat_store["rooms"][room_id]= room_data
        self.save_qa_chat_store()

        return room_id
    
    def add_message(self, room_id, user_name, message):
        """Add a message to a QA room"""
        if room_id not in self.qa_chat_store["rooms"]:
            return None
        
        message_data= {
            "id": str(uuid.uuid4()),
            "user": user_name,
            "content": message,
            "timestamp":datetime.now().isoformat()
        }
        self.qa_chat_store["rooms"][room_id]["messages"].append(message_data)
        self.save_qa_chat_store()

        return message_data
    
    
    def get_message(self,room_id, limit=50 ):
        """Get the most recent messages from a QA room"""
        if room_id not in self.qa_chat_store["rooms"]:
            return []
        messages= self.qa_chat_store["rooms"][room_id]["messages"]
        return messages[-limit:] if len(messages)> limit else messages
    

    def get_qa_room(self):
        """Get a all QA Rooms"""
        rooms= []

        for room_id, room_data in self.qa_chat_store["rooms"].items():
            rooms.append({
                "id": room_id,
                "name": room_data.get("name", "Unnamed Room"),
                "creator": room_data.get("creator", "Unknown"),
                "created_at": room_data_get("created_at", "")
            })

            # Sort By creation date newest firest
            rooms.sort(key= lambda x:x["created_at"], reverse= True)
            return rooms


    def delete_qa_room(self, room_id):
        """Delete a QA chat room"""
        if room_id in self.qa_chat_store["rooms"]:
            del self.qa_chat_store["rooms"][room_id]
            self.save_qa_chat_store()
            return True
        return False