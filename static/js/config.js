// Configuração global para requisições AJAX
window.apiConfig = {
    baseUrl: '',  // URL base vazia para usar caminhos relativos
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
    }
};

// Função auxiliar para fazer requisições
window.api = {
    request: async function(url, options = {}) {
        const defaultOptions = {
            headers: window.apiConfig.headers,
            credentials: 'same-origin'  // Incluir cookies na requisição
        };
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, finalOptions);
            const contentType = response.headers.get('content-type');
            
            if (!response.ok) {
                let errorMessage;
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.error || `HTTP error! status: ${response.status}`;
                } else {
                    const errorText = await response.text();
                    console.error('Erro na resposta (não-JSON):', errorText);
                    errorMessage = `HTTP error! status: ${response.status}`;
                }
                throw new Error(errorMessage);
            }
            
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                console.warn('Resposta não é JSON:', await response.text());
                return null;
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    },
    
    get: function(url) {
        return this.request(url);
    },
    
    post: function(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    put: function(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    delete: function(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};
