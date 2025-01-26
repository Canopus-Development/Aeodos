if (!window.Prism) {
    window.Prism = {
        languages: {
            bash: {
                'comment': /#.*/,
                'string': /("|')(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
                'variable': /\$[\w-]+/,
                'function': /\b(?:curl|wget|git)\b/,
                'keyword': /\b(?:POST|GET|PUT|DELETE)\b/
            },
            python: {
                'comment': /#.*/,
                'string': /(?:'''[\s\S]*?'''|'[^']*'|"""[\s\S]*?"""|"[^"]*")/,
                'keyword': /\b(?:import|from|def|class|return|async|await)\b/,
                'function': /\b(?:print|requests?\.(?:get|post|put|delete))\b/,
                'boolean': /\b(?:True|False|None)\b/
            },
            json: {
                'property': /"(?:\\.|[^\\"\r\n])*"(?=\s*:)/,
                'string': /"(?:\\.|[^\\"\r\n])*"/,
                'number': /\b0x[\dA-Fa-f]+\b|-?\b\d*\.?\d+\b/,
                'punctuation': /[{}[\]]/,
                'operator': /:/,
                'boolean': /\b(?:true|false|null)\b/
            },
            php: {
                'comment': /\/\*[\s\S]*?\*\/|\/\/.*/,
                'string': /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
                'keyword': /\b(?:and|or|xor|array|as|break|case|cfunction|class|const|continue|declare|default|die|do|else|elseif|enddeclare|endfor|endforeach|endif|endswitch|endwhile|extends|for|foreach|function|include|include_once|global|if|new|return|static|switch|use|require|require_once|var|while|abstract|interface|public|implements|private|protected|parent|throw|null|echo|print|trait|namespace|final|yield|goto|instanceof|finally|try|catch)\b/i,
                'boolean': /\b(?:true|false)\b/i,
                'number': /\b0x[\da-f]+\b|(?:\b\d+\.?\d*|\B\.\d+)(?:e[+-]?\d+)?/i,
                'operator': /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
                'punctuation': /[{}[\];(),.:]/
            },
            go: {
                'comment': /\/\/.*|\/\*[\s\S]*?\*\//,
                'string': /(["'`])(?:\\[\s\S]|(?!\1)[^\\])*\1/,
                'keyword': /\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|import|interface|map|package|range|return|select|struct|switch|type|var)\b/,
                'boolean': /\b(?:_|iota|nil|true|false)\b/,
                'number': /(?:\b0x[a-f\d]+|(?:\b\d+\.?\d*|\B\.\d+)(?:e[-+]?\d+)?)i?/i,
                'operator': /[*\/%^!=]=?|\+[=+]?|-[=-]?|\|[=|]?|&(?:=|&|\^=?)?|>(?:>=?|=)?|<(?:<=?|=|-)?|:=|\.\.\./,
                'punctuation': /[{}[\];(),.:]/
            }
        },

        highlightAll: function() {
            document.querySelectorAll('pre code').forEach(block => {
                const language = block.className.match(/language-(\w+)/)?.[1];
                if (language && this.languages[language]) {
                    block.innerHTML = this.highlight(block.textContent, language);
                }
            });
        },

        highlight: function(text, language) {
            const grammar = this.languages[language];
            let result = text;

            for (const tokenName in grammar) {
                const pattern = grammar[tokenName];
                result = result.replace(pattern, match => 
                    `<span class="token ${tokenName}">${match}</span>`
                );
            }

            return result;
        }
    };
}
