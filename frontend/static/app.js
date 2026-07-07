document.addEventListener('alpine:init', () => {
    Alpine.data('chatApp', () => ({
        messages: [
            { role: 'agent', content: 'Hello! I am the MWIS Weather Agent. How can I help you plan your mountain outing today?' }
        ],
        currentMessage: '',
        isLoading: false,
        
        // Dev Tool States
        regionQuery: '',
        regionOutput: '',
        isQueryingRegion: false,
        
        dateQuery: '',
        dateOutput: '',
        isQueryingDate: false,

        // Replace with production ADK backend URL if needed
        adkEndpoint: 'http://localhost:8080/a2a/mwis-agent',

        init() {
            // Initialization logic if any
        },

        async sendMessage() {
            if (!this.currentMessage.trim()) return;

            const userText = this.currentMessage.trim();
            this.messages.push({ role: 'user', content: userText });
            this.currentMessage = '';
            this.isLoading = true;

            this.scrollToBottom();

            try {
                // The ADK Agent accepts POST requests to /a2a/mwis-agent
                const response = await fetch(this.adkEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        inputs: { input: userText } // Follow ADK input spec if necessary
                    })
                });

                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}`);
                }

                const data = await response.json();
                
                // Assuming ADK output format
                let agentContent = "No response text found.";
                if (data.outputs && data.outputs.output) {
                    agentContent = data.outputs.output;
                } else if (data.response) { // fallback
                    agentContent = data.response;
                }

                this.messages.push({ role: 'agent', content: agentContent });

            } catch (error) {
                console.error("Error communicating with agent:", error);
                this.messages.push({ 
                    role: 'agent', 
                    content: `Error: Unable to connect to the agent backend. Please ensure the ADK server is running. (${error.message})` 
                });
            } finally {
                this.isLoading = false;
                this.scrollToBottom();
            }
        },

        scrollToBottom() {
            setTimeout(() => {
                const historyBox = document.getElementById('chat-history');
                if (historyBox) {
                    historyBox.scrollTop = historyBox.scrollHeight;
                }
            }, 50);
        },

        async submitRegion() {
            if (!this.regionQuery.trim()) return;
            this.isQueryingRegion = true;
            this.regionOutput = 'Loading...';
            
            try {
                const url = new URL('/api/query_region', window.location.origin);
                url.searchParams.append('q', this.regionQuery.trim());
                
                const response = await fetch(url);
                const data = await response.json();
                
                this.regionOutput = JSON.stringify(data, null, 2);
            } catch (error) {
                this.regionOutput = `Error: ${error.message}`;
            } finally {
                this.isQueryingRegion = false;
            }
        },

        async submitDate() {
            if (!this.dateQuery.trim()) return;
            this.isQueryingDate = true;
            this.dateOutput = 'Loading...';
            
            try {
                const url = new URL('/api/query_date', window.location.origin);
                url.searchParams.append('q', this.dateQuery.trim());
                
                const response = await fetch(url);
                const data = await response.json();
                
                this.dateOutput = JSON.stringify(data, null, 2);
            } catch (error) {
                this.dateOutput = `Error: ${error.message}`;
            } finally {
                this.isQueryingDate = false;
            }
        }
    }));
});
