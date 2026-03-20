// Vercel Serverless Function - 获取CBA赛程数据
// 访问: /api/schedule

export default async function handler(req, res) {
    // 设置CORS头
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // 从新浪体育获取数据
        const response = await fetch('https://cba.sports.sina.com.cn/cba/schedule/all/', {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 获取GBK编码的响应
        const buffer = await response.arrayBuffer();
        const html = decodeGBK(buffer);

        // 解析赛程数据
        const schedule = parseSchedule(html);

        res.status(200).json({
            success: true,
            data: schedule,
            updated: new Date().toISOString()
        });

    } catch (error) {
        console.error('获取数据失败:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
}

// 解码GBK编码
function decodeGBK(buffer) {
    const uint8Array = new Uint8Array(buffer);
    // GBK to UTF-8 转换映射表 (简化版，用于中文字符)
    let result = '';
    let i = 0;

    while (i < uint8Array.length) {
        let byte = uint8Array[i];

        if (byte < 0x80) {
            // ASCII字符
            result += String.fromCharCode(byte);
            i++;
        } else if (byte >= 0x81 && byte <= 0xFE) {
            // GBK双字节字符
            if (i + 1 < uint8Array.length) {
                const byte2 = uint8Array[i + 1];
                // 使用TextDecoder (Vercel支持)
                const gbkBytes = new Uint8Array([byte, byte2]);
                try {
                    const decoder = new TextDecoder('gbk');
                    result += decoder.decode(gbkBytes);
                } catch (e) {
                    result += '?';
                }
                i += 2;
            } else {
                i++;
            }
        } else {
            result += String.fromCharCode(byte);
            i++;
        }
    }

    return result;
}

// 解析赛程HTML
function parseSchedule(html) {
    const schedule = [];

    // 提取主表格
    const tableMatch = html.match(/<div class="part part02[^>]*>(.*?)<\/div>\s*<\/div>\s*<!-- part02 end/s);
    if (!tableMatch) return schedule;

    const tableHtml = tableMatch[1];

    // 提取所有行
    const rowRegex = /<tr[^>]*class="(odd|even)"[^>]*>(.*?)<\/tr>/gs;
    let rowMatch;

    while ((rowMatch = rowRegex.exec(tableHtml)) !== null) {
        const rowContent = rowMatch[2];

        // 提取单元格
        const cellRegex = /<td[^>]*>(.*?)<\/td>/gs;
        const cells = [];
        let cellMatch;

        while ((cellMatch = cellRegex.exec(rowContent)) !== null) {
            let text = cellMatch[1]
                .replace(/<[^>]+>/g, '')
                .trim()
                .replace(/&nbsp;/g, ' ')
                .replace(/&#58;/g, ':');
            cells.push(text);
        }

        if (cells.length >= 5) {
            const [round, datetime, home, score, away] = cells;
            const today = new Date().toISOString().split('T')[0];
            const gameDate = datetime.split(' ')[0];

            let status;
            if (score.includes(':') && !score.includes('VS')) {
                status = '已结束';
            } else if (gameDate === today) {
                status = '进行中';
            } else if (new Date(gameDate) < new Date(today)) {
                status = '已结束';
            } else {
                status = '未开始';
            }

            schedule.push({
                round,
                datetime,
                home,
                score,
                away,
                status
            });
        }
    }

    return schedule;
}