use std::error::Error;
use std::io::BufReader;
use glob::glob;
use scraper::{Html, Selector};
use std::fs::{File};
use std::io::{Read};

fn main() -> Result<(), Box<dyn Error>> {
    for entry in glob("../../data/original/covid-2022*.html")? {
        let path = entry?;
        println!("{}", path.display());

        let input = File::open(path)?;
        let mut buffered = BufReader::new(input);
        let mut html = String::new();
        buffered.read_to_string(&mut html).unwrap();
        let html = Html::parse_document(&html);
        let selector = Selector::parse("#current-confirmed-cases-covid-19 > div.site-content.wrapper > div > div > div > article > div > table th,td").unwrap();
        //let selector2 = Selector::parse("th,td").unwrap();
        for element in html.select(&selector) {
            println!("{}", element.inner_html());
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