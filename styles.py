styles = """
    <style>
    body {
        display: flex;
        flex-direction: row;
        gap: 20px;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(10, 30px);
        grid-template-rows: repeat(10, 30px);
        gap: 2px;
        margin-bottom: 20px;
    }
    .grid-item {
        width: 30px;
        height: 30px;
        border: 1px solid black;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .agent {
        background-color: blue;
    }
    .treasure {
        background-color: red;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .message-bubble {
        border-radius: 10px;
        padding: 10px;
        max-width: 70%;
        word-wrap: break-word;
    }
    .agent1 {
        background-color: #DCF8C6;
        align-self: flex-start;
    }
    .agent2 {
        background-color: #FFD1D1;
        align-self: flex-end;
    }
    .agent-name {
        font-weight: bold;
        margin-bottom: 5px;
    }
    </style>
"""
