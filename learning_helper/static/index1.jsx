import React from 'react';
import ReactDOM from 'react-dom/client';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mic, UploadCloud } from "lucide-react";
import { useState, useEffect } from 'react';

function LearningAssistant() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [feedback, setFeedback] = useState("");
    const [progress, setProgress] = useState({ correct: 0, total: 0 });

    useEffect(() => {
        fetchQuestion();
        fetchProgress();
    }, []);

    const fetchQuestion = async () => {
        const res = await fetch("/api/question");
        const data = await res.json();
        setQuestion(data.question);
    };

    const submitAnswer = async () => {
        const res = await fetch("/api/answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer }),
        });
        const data = await res.json();
        setFeedback(data.feedback);
        fetchProgress();
    };

    const fetchProgress = async () => {
        const res = await fetch("/api/progress");
        const data = await res.json();
        setProgress(data);
    };

    return (
        <div className="max-w-3xl mx-auto p-6 space-y-4">
            <h1 className="text-2xl font-bold">个人强化学习助手</h1>
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">问题：</h2>
                <p className="bg-gray-100 p-4 rounded">{question}</p>
            </div>
            <Textarea
                placeholder="输入你的回答..."
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
            />
            <div className="flex gap-2">
                <Button onClick={submitAnswer}>提交回答</Button>
                <Button variant="outline" onClick={fetchQuestion}>
                    下一个问题
                </Button>
            </div>
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">反馈：</h2>
                <p className="bg-green-100 p-4 rounded">{feedback}</p>
            </div>
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">学习进度：</h2>
                <p>
                    正确率: {progress.correct}/{progress.total}
                </p>
            </div>
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">上传知识库：</h2>
                <Input type="file" />
                <Button variant="outline">
                    <UploadCloud className="mr-2" /> 上传文件
                </Button>
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<LearningAssistant />);