using System;
using System.Collections.Generic;

namespace CalculatorApp
{
    public class Calculator
    {
        public static double CalculateTotal(List<double> prices)
        {
            if (prices == null)
                throw new ArgumentNullException(nameof(prices));
        foreach (double price in prices)
        {
                if (price < 0)
                    throw new ArgumentException("Alle Preise müssen nicht-negativ sein.", nameof(prices));
        }

            double sum = 0;
            foreach (double price in prices)
    {
                sum += price;
    }
            return sum;
        }

        public static double Add(double a, double b)
    {
            return a + b;
        }

        public static double Subtract(double a, double b)
        {
            return a - b;
        }

        public static double Multiply(double a, double b)
            {
            return a * b;
        }

        public static double Divide(double a, double b)
                    {
            if (b == 0)
                throw new DivideByZeroException("Cannot divide by zero.");
            return a / b;
                    }

        public static double Power(double baseValue, double exponent)
            {
            return Math.Pow(baseValue, exponent);
            }

        public static double Modulo(double a, double b)
        {
            if (b == 0)
                throw new DivideByZeroException("Cannot compute modulo with zero divisor.");
            return a % b;
    }

        public static double SquareRoot(double value)
        {
            if (value < 0)
                throw new ArgumentException("Der Wert darf nicht negativ sein.", nameof(value));
            return Math.Sqrt(value);
}

        public static void Main(string[] args)
        {
            Console.WriteLine("========================");
            Console.WriteLine("   Taschenrechner");
            Console.WriteLine("========================");
            Console.WriteLine();

            while (true)
            {
                Console.Write("Erste Zahl: ");
                string inputA = Console.ReadLine();
                if (inputA.ToLower() == "q") break;
                double a = Convert.ToDouble(inputA);

                Console.Write("Zweite Zahl: ");
                string inputB = Console.ReadLine();
                if (inputB.ToLower() == "q") break;
                double b = Convert.ToDouble(inputB);

                Console.WriteLine();
                Console.WriteLine("Wähle eine Operation:");
                Console.WriteLine("  +   Addition");
                Console.WriteLine("  -   Subtraktion");
                Console.WriteLine("  *   Multiplikation");
                Console.WriteLine("  /   Division");
                Console.WriteLine("  ^   Potenz (a^b)");
                Console.WriteLine("  %   Modulo (Rest der Division)");
                Console.Write("> ");
                string op = Console.ReadLine();

                double result = 0;
                bool success = true;

                switch (op)
                {
                    case "+":
                        result = Add(a, b);
                        break;
                    case "-":
                        result = Subtract(a, b);
                        break;
                    case "*":
                        result = Multiply(a, b);
                        break;
                    case "/":
                        try
                        {
                            result = Divide(a, b);
                        }
                        catch (DivideByZeroException ex)
                        {
                            Console.WriteLine($"Fehler: {ex.Message}");
                            success = false;
                        }
                        break;
                    case "^":
                        result = Power(a, b);
                        break;
                    case "%":
                        try
                        {
                            result = Modulo(a, b);
                        }
                        catch (DivideByZeroException ex)
                        {
                            Console.WriteLine($"Fehler: {ex.Message}");
                            success = false;
                        }
                        break;
                    default:
                        Console.WriteLine("Ungültige Operation!");
                        success = false;
                        break;
                }

                if (success)
                {
                    Console.WriteLine();
                    Console.WriteLine($"Ergebnis: {result}");
                }

                Console.WriteLine();
            }

            Console.WriteLine("Programm beendet.");
        }
    }
}

