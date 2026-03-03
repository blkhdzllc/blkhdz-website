<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BLKHDZ | Elite Shop</title>
    <style>
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
        .hero { 
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), url('./hero-parallax.jpg'); 
            height: 450px; background-attachment: fixed; background-size: cover; background-position: center;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .logo { width: 220px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(255,204,0,0.5)); }
        .section-header { border-left: 6px solid #ffcc00; padding-left: 20px; margin: 50px 20px 30px; color: #ffcc00; text-transform: uppercase; letter-spacing: 3px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; padding: 0 20px 50px; }
        .card { background: #121212; border: 1px solid #222; border-radius: 15px; padding: 25px; text-align: center; transition: 0.3s; }
        .card:hover { border-color: #ffcc00; transform: scale(1.02); }
        .card img { width: 100%; height: 220px; object-fit: contain; margin-bottom: 20px; border-radius: 10px; background: #fff; }
        .price { color: #00ff88; font-size: 2rem; font-weight: 900; margin: 15px 0; }
        .btn-group { display: flex; flex-direction: column; gap: 12px; }
        .btn { padding: 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 0.95rem; text-transform: uppercase; }
        .btn-ebay { background: #0053d6; color: white; }
        .btn-amazon { background: #ff9900; color: black; }
    </style>
</head>
<body>

    <div class="hero">
        <img src="./blkhdz.png" alt="BLKHDZ" class="logo">
    </div>

    <h2 class="section-header">2026 Watchlist</h2>
    <div id="watchlist-grid" class="grid"></div>

    <h2 class="section-header">Elite LEGO Inventory</h2>
    <div id="elite-grid" class="grid"></div>

    <h2 class="section-header">Precision Diecast</h2>
    <div id="diecast-grid" class="grid"></div>

    <script>
        fetch('data.json?v=' + Date.now())
        .then(res => res.json())
        .then(data => {
            data.forEach(item => {
                const card = `
                    <div class="card">
                        <img src="${item.image_url}" onerror="this.src='./placeholder.jpg'">
                        <h3>${item.name}</h3>
                        <div class="price">$${item.ebay_avg_price}</div>
                        <div class="btn-group">
                            <a href="${item.ebay_link}" class="btn btn-ebay" target="_blank">View on eBay</a>
                            <a href="https://www.amazon.com/s?k=LEGO+${item.set_num}" class="btn btn-amazon" target="_blank">View on Amazon</a>
                        </div>
                    </div>`;
                
                if (item.type === '2026') document.getElementById('watchlist-grid').innerHTML += card;
                else if (item.type === 'diecast') document.getElementById('diecast-grid').innerHTML += card;
                else document.getElementById('elite-grid').innerHTML += card;
            });
        });
    </script>
</body>
</html>
