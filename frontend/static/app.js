/*
 * MWIS Agent (c) by Mehmet Rahmi Karatay
 *
 * MWIS Agent is licensed under a
 * Creative Commons Attribution-ShareAlike 4.0 International License.
 *
 * You should have received a copy of the license along with this
 * work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
 */

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

        // Point to the local backend proxy
        adkEndpoint: '/api/chat',
        mwisEnv: 'production',

        async init() {
            try {
                const response = await fetch('/api/config');
                if (response.ok) {
                    const config = await response.json();
                    this.mwisEnv = config.mwis_env;
                }
            } catch (error) {
                console.error("Error fetching config:", error);
            }
        },

        async sendMessage() {
            if (!this.currentMessage.trim()) return;

            const userText = this.currentMessage.trim();
            this.messages.push({ role: 'user', content: userText });
            this.currentMessage = '';
            this.isLoading = true;

            this.scrollToBottom();

            try {
                // The ADK Agent proxy endpoint
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
