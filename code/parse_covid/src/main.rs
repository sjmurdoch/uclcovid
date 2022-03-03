use std::error::Error;
use std::io::BufReader;
use glob::glob;
use scraper::{Html, Selector};
use std::fs::{File};
use std::io::{Read};

fn show(last: &[String]) {
    for v in last {
        print!("{}, ", v);
    }
    println!();
}

fn main() -> Result<(), Box<dyn Error>> {
    let selector = Selector::parse("#current-confirmed-cases-covid-19 > div.site-content.wrapper > div
    > div > div > article > div > table th,td").unwrap();
    let mut last: [String; 23] = Default::default();

    for entry in glob("../../data/original/covid-*.html")? {
        let path = entry?;
        println!("Reading {}", path.display());

        let input = File::open(&path)?;
        let mut buffered = BufReader::new(input);
        let mut html = String::new();
        buffered.read_to_string(&mut html).unwrap();
        let html = Html::parse_document(&html);

        //let selector2 = Selector::parse("th,td").unwrap();

        let mut changed = false;
        for (i, element) in html.select(&selector).enumerate() {
            let text = element.text()
                .collect::<Vec<&str>>()
                .join(" ");
            if last[i] != text {
                last[i] = text;
                changed = true;
            }
            //println!("{}", element.inner_html());
        }
        if changed {
            show(&last);
        } else {
            println!("unchanged: {}", path.display())
        }

        //let soup = Soup::from_reader(buffered)?;
        //let h1 = soup.class("box").class("box").find().expect("Could not find node box");
        //let h2 = h1.tag("h2").find().expect("Could not find node h2");
        //println!("{}", h2.display());
        //header = soup.select_one('.box > h2:nth-child(1)')
        //table = soup.select_one('#current-confirmed-cases-covid-19 > div.site-content.wrapper > div > div > div > article > div > table')
    }

    Ok(())
}